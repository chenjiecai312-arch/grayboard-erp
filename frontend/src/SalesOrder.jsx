import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  Form, Input, Button, Table, message, Modal, Select, Space, DatePicker,
  InputNumber, Popconfirm, Tag, AutoComplete, Divider, Cascader, Checkbox
} from 'antd';
import { api } from './api';
import dayjs from 'dayjs';
import SalesOrderPrint from './SalesOrderPrint';
import StockPickListPrint from './StockPickListPrint';

const STATUS_MAP = {
  draft: { label: '草稿', color: 'default' },
  pending: { label: '待发货', color: 'orange' },
  shipped: { label: '已发货', color: 'blue' },
  completed: { label: '已完成', color: 'green' },
  cancelled: { label: '已取消', color: 'default' },
}

// 金额大写转换
function amountToChinese(num) {
  if (!num || num === 0) return '零元整';
  const digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖'];
  const units = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿'];
  const intPart = Math.floor(num);
  const decPart = Math.round((num - intPart) * 100);
  let result = '';
  const intStr = String(intPart);
  for (let i = 0; i < intStr.length; i++) {
    const d = parseInt(intStr[i]);
    const u = intStr.length - 1 - i;
    if (d !== 0) {
      result += digits[d] + units[u];
    } else if (result && !result.endsWith('零') && u !== 4) {
      result += '零';
    }
    if (u === 4 && !result.endsWith('万')) result += '万';
  }
  result = result.replace(/零+$/, '').replace(/零万/, '万') + '元';
  if (decPart === 0) {
    result += '整';
  } else {
    const jiao = Math.floor(decPart / 10);
    const fen = decPart % 10;
    if (jiao > 0) result += digits[jiao] + '角';
    if (fen > 0) result += digits[fen] + '分';
  }
  return result;
}

// 创建空明细行
function createEmptyItem(lineNo) {
  return {
    line_no: lineNo,
    product_name: '',
    spec: '',
    length: 0,
    width: 0,
    nominal_gram: 0,
    actual_gram: 0,
    unit: '张',
    quantity: 0,
    ton_price: 0,
    unit_price: 0,
    amount: 0,
    cost: 0,
    waste_rate: 3,        // 损耗率默认3%
    lamination_fee: 300,  // 裱工费默认300元/吨
    cost_layers: '',      // 保存成本层详情(JSON)
    remark: '',
  };
}

// 计算单价：面积(m²) × 虚克(g/m²) × 吨价(元/吨) / 1000000 = 元/张
function calcUnitPrice(length, width, nominalGram, tonPrice) {
  const area = (Number(length) || 0) * (Number(width) || 0) / 1000000; // m²
  return area * (Number(nominalGram) || 0) * (Number(tonPrice) || 0) / 1000000;
}

export default function SalesOrder() {
  const [orderList, setOrderList] = useState([]);
  const [customerList, setCustomerList] = useState([]);
  const [productList, setProductList] = useState([]);
  const [pnList, setPnList] = useState([]); // 成品品名列表
  const [rollList, setRollList] = useState([]); // 卷筒仓库存
  const [rollNameList, setRollNameList] = useState([]); // 卷筒仓品名
  const [rollCategoryList, setRollCategoryList] = useState([]); // 卷筒仓物理分类
  const [loading, setLoading] = useState(false);

  // 搜索
  const [searchCustomer, setSearchCustomer] = useState("");
  const [searchCustomerId, setSearchCustomerId] = useState(null); // 按客户筛选
  const [searchField, setSearchField] = useState(""); // 通用筛选字段
  const [searchValue, setSearchValue] = useState(""); // 通用筛选值
  const [searchStatus, setSearchStatus] = useState(undefined);
  const [searchDateRange, setSearchDateRange] = useState(null);

  // 新增/编辑弹窗
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editForm] = Form.useForm();
  const [items, setItems] = useState([createEmptyItem(1)]);

  // 打印
  const [printData, setPrintData] = useState(null);
  const [printOpen, setPrintOpen] = useState(false);

  // 成本测算弹窗
  const [costModalOpen, setCostModalOpen] = useState(false);
  const [costEditIdx, setCostEditIdx] = useState(null);
  const [costLayers, setCostLayers] = useState([
    { layer_name: '', gram: 0, width: 0, ton_price: 0 },
  ]);
  const [costWasteRate, setCostWasteRate] = useState(0); // 损耗率（%）
  const [costLaminationFee, setCostLaminationFee] = useState(0); // 裱工费（元/吨）

  // 选择成品弹窗
  const [productModalOpen, setProductModalOpen] = useState(false);
  const [productSelectIdx, setProductSelectIdx] = useState(null);

  // 待出库订单弹窗
  const [pendingModalOpen, setPendingModalOpen] = useState(false);
  const [pickListOrders, setPickListOrders] = useState([]); // 备货单打印的订单列表
  const [shipLoading, setShipLoading] = useState(false);
  const [showPickListPrint, setShowPickListPrint] = useState(false);
  const [pendingList, setPendingList] = useState([]);

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    try {
      const params = {};
      if (searchCustomer) params.customer_name = searchCustomer;
      if (searchCustomerId) params.customer_id = searchCustomerId;
      if (searchField && searchValue) {
        params.search_field = searchField;
        params.search_value = searchValue;
      }
      if (searchStatus) params.status = searchStatus;
      if (searchDateRange && searchDateRange.length === 2) {
        params.start_date = searchDateRange[0].format('YYYY-MM-DD');
        params.end_date = searchDateRange[1].format('YYYY-MM-DD');
      }
      const res = await api.get("/api/sales_order", { params });
      setOrderList(res.data);
    } catch (err) {
      message.error("加载订单失败：" + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  }

  const loadDict = async () => {
    try {
      const [cRes, pRes, rRes, rnRes, pcRes, pnRes] = await Promise.all([
        api.get("/api/customer"),
        api.get("/api/product"),
        api.get("/api/rawroll"),
        api.get("/api/product_name"),
        api.get("/api/physical_category"),
        api.get("/api/product_name_finished")
      ]);
      setCustomerList(cRes.data);
      setProductList(pRes.data);
      setRollList(rRes.data);
      setRollNameList(rnRes.data);
      setRollCategoryList(pcRes.data);
      setPnList(pnRes.data);
    } catch (e) {
      console.error(e);
    }
  }

  useEffect(() => {
    loadData();
    loadDict();
  }, []);

  // 从成品库获取品名列表（用于AutoComplete）
  const productNameOptions = useMemo(() => {
    const names = new Set();
    productList.forEach(p => {
      const name = p.product_name_id || p.spec || '';
      if (name) names.add(String(name));
    });
    return Array.from(names).map(n => ({ value: n, label: n }));
  }, [productList]);

  // 卷筒仓级联选择数据：严格按照物理分类四级树形结构 → 最后一级挂具体卷筒库存
  const rollCascaderOptions = useMemo(() => {
    // 1. 构建物理分类树形结构（四级）
    const buildCategoryTree = () => {
      const map = {};
      const roots = [];
      rollCategoryList.forEach(c => {
        map[c.id] = { ...c, children: [] };
      });
      rollCategoryList.forEach(c => {
        if (c.parent_id && map[c.parent_id]) {
          map[c.parent_id].children.push(map[c.id]);
        } else if (!c.parent_id) {
          roots.push(map[c.id]);
        }
      });
      return roots;
    };

    // 2. 在分类树的叶子节点挂卷筒库存
    const categoryTree = buildCategoryTree();

    const attachRolls = (nodes) => {
      return nodes.map(node => {
        if (node.children && node.children.length > 0) {
          // 非叶子节点，递归
          return {
            value: `cat_${node.id}`,
            label: node.name,
            children: attachRolls(node.children),
          };
        } else {
          // 叶子节点（四级分类），挂该分类下的卷筒库存
          const rolls = rollList.filter(r => r.category_id === node.id);
          if (rolls.length === 0) {
            return {
              value: `cat_${node.id}`,
              label: `${node.name}（无库存）`,
              disabled: true,
            };
          }
          return {
            value: `cat_${node.id}`,
            label: node.name,
            children: rolls.map(r => {
              const pn = rollNameList.find(n => n.id === r.product_name_id);
              const name = pn?.name || String(r.product_name_id) || '未知';
              return {
                value: `roll_${r.id}`,
                label: `${name} 库存${Number(r.stock_weight).toFixed(2)}吨`,
                roll: r,
                name: name,
              };
            }),
          };
        }
      });
    };

    return attachRolls(categoryTree);
  }, [rollList, rollNameList, rollCategoryList]);

  // 明细合计
  const totalAmount = useMemo(() => {
    return items.reduce((sum, it) => sum + (Number(it.amount) || 0), 0);
  }, [items]);

  // 成本测算：实克
  const costActualGram = useMemo(() => {
    return costLayers.reduce((sum, l) => sum + (Number(l.gram) || 0), 0);
  }, [costLayers]);

  // 成本测算：每张成本（按实际幅宽计算，包含损耗率和裱工费）
  const costPerPiece = useMemo(() => {
    if (costEditIdx === null || !items[costEditIdx]) return 0;
    const length = Number(items[costEditIdx].length) || 0;
    const width = Number(items[costEditIdx].width) || 0;
    const actualGram = costLayers.reduce((sum, l) => sum + (Number(l.gram) || 0), 0);

    // 1. 纸张总成本（按实际幅宽计算，已包含幅宽差异损耗）
    const paperCost = costLayers.reduce((sum, l) => {
      const layerCost = length * (Number(l.width) || 0) * (Number(l.gram) || 0) * (Number(l.ton_price) || 0) / 1e12;
      return sum + layerCost;
    }, 0);

    // 2. 损耗成本（纸张成本 × 损耗率%）
    const wasteCost = paperCost * (Number(costWasteRate) || 0) / 100;

    // 3. 裱工费（元/吨）：每张重量(吨) = 长×宽×实克/1e12，裱工费 = 重量×单价
    const weightPerPiece = length * width * actualGram / 1e12;
    const laminationCost = weightPerPiece * (Number(costLaminationFee) || 0);

    return paperCost + wasteCost + laminationCost;
  }, [costLayers, costEditIdx, items, costWasteRate, costLaminationFee]);

  // 成本测算：损耗信息（每层幅宽与成品宽的差异）
  const costWasteInfo = useMemo(() => {
    if (costEditIdx === null || !items[costEditIdx]) return [];
    const productWidth = Number(items[costEditIdx].width) || 0;
    return costLayers.map((l, idx) => {
      const layerWidth = Number(l.width) || 0;
      const waste = Math.max(0, layerWidth - productWidth);
      return { idx, layerWidth, productWidth, waste, wasteRate: productWidth > 0 ? waste / productWidth : 0 };
    });
  }, [costLayers, costEditIdx, items]);

  // 添加明细行
  const addItemRow = () => {
    setItems([...items, createEmptyItem(items.length + 1)]);
  }

  // 删除明细行
  const removeItemRow = (idx) => {
    if (items.length <= 1) {
      message.warning("至少保留一行明细");
      return;
    }
    const newItems = items.filter((_, i) => i !== idx);
    newItems.forEach((it, i) => it.line_no = i + 1);
    setItems(newItems);
  }

  // 更新明细行（自动计算单价和金额，触发自动保存）
  const updateItemRow = (idx, field, value) => {
    const newItems = [...items];
    newItems[idx][field] = value;
    // 如果改了长/宽/虚克/吨价，重新计算单价
    if (['length', 'width', 'nominal_gram', 'ton_price'].includes(field)) {
      newItems[idx].unit_price = calcUnitPrice(
        newItems[idx].length, newItems[idx].width,
        newItems[idx].nominal_gram, newItems[idx].ton_price
      );
    }
    // 如果改了数量或单价，重新计算金额
    if (['quantity', 'unit_price', 'length', 'width', 'nominal_gram', 'ton_price'].includes(field)) {
      newItems[idx].amount = (Number(newItems[idx].quantity) || 0) * (Number(newItems[idx].unit_price) || 0);
    }
    setItems(newItems);
    // 触发自动保存
    if (editingId) triggerAutoSave();
  }

  // 选择货品名称后，尝试从成品库带出信息
  const handleProductSelect = (idx, value) => {
    updateItemRow(idx, 'product_name', value);
    const matched = productList.find(p => String(p.product_name_id || p.spec || '') === String(value));
    if (matched) {
      // 尝试从spec解析长宽，格式如 787*1092（宽×长）
      if (matched.spec) {
        const m = String(matched.spec).match(/(\d+)\s*[*xX×]\s*(\d+)/);
        if (m) {
          updateItemRow(idx, 'width', Number(m[1]));
          updateItemRow(idx, 'length', Number(m[2]));
        }
      }
      updateItemRow(idx, 'spec', matched.spec || '');
      updateItemRow(idx, 'unit', matched.unit || '张');
      if (matched.actual_gram) updateItemRow(idx, 'nominal_gram', matched.actual_gram);
    }
  }

  // 打开选择成品弹窗
  const openProductSelect = (idx) => {
    setProductSelectIdx(idx);
    setProductModalOpen(true);
  }

  // 从成品库选择成品
  const handleSelectProduct = (product) => {
    const idx = productSelectIdx;
    // 存 product_id 锁定具体成品
    updateItemRow(idx, 'product_id', product.id);
    // 品名显示名称
    const pnName = pnList.find(p => p.id === product.product_name_id)?.name || product.product_name_id || '';
    updateItemRow(idx, 'product_name', pnName);
    updateItemRow(idx, 'spec', product.spec || '');
    updateItemRow(idx, 'unit', product.unit || '张');
    if (product.spec) {
      const m = String(product.spec).match(/(\d+\.?\d*)\s*[*xX×]\s*(\d+\.?\d*)/);
      if (m) {
        updateItemRow(idx, 'width', Number(m[1]));
        updateItemRow(idx, 'length', Number(m[2]));
      }
    }
    if (product.actual_gram) updateItemRow(idx, 'nominal_gram', product.actual_gram);
    setProductModalOpen(false);
    message.success("已从成品库选择");
  }

  // 打开成本测算弹窗（回显之前的数据）
  const openCostCalc = (idx) => {
    setCostEditIdx(idx);
    const item = items[idx];
    // 回显之前的成本层
    if (item.cost_layers) {
      try {
        const parsed = JSON.parse(item.cost_layers);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setCostLayers(parsed);
        } else {
          setCostLayers([{ layer_name: '', gram: 0, width: item.width || 0, ton_price: 0 }]);
        }
      } catch (e) {
        setCostLayers([{ layer_name: '', gram: 0, width: item.width || 0, ton_price: 0 }]);
      }
    } else {
      setCostLayers([{ layer_name: '', gram: 0, width: item.width || 0, ton_price: 0 }]);
    }
    // 回显损耗率和裱工费，默认3%和300
    setCostWasteRate(item.waste_rate !== undefined && item.waste_rate !== null ? item.waste_rate : 3);
    setCostLaminationFee(item.lamination_fee !== undefined && item.lamination_fee !== null ? item.lamination_fee : 300);
    setCostModalOpen(true);
  }

  // 添加成本层
  const addCostLayer = () => {
    if (costLayers.length >= 5) {
      message.warning("最多5裱（5层）");
      return;
    }
    setCostLayers([...costLayers, { layer_name: '', gram: 0, width: 0, ton_price: 0 }]);
  }

  // 删除成本层
  const removeCostLayer = (idx) => {
    if (costLayers.length <= 1) {
      message.warning("至少保留一层");
      return;
    }
    setCostLayers(costLayers.filter((_, i) => i !== idx));
  }

  // 更新成本层
  const updateCostLayer = (idx, field, value) => {
    const newLayers = [...costLayers];
    newLayers[idx][field] = value;
    setCostLayers(newLayers);
  }

  // 从卷筒仓级联选择后，自动带出纸名（含第一二级分类路径）、克重、幅宽
  const handleRollCascaderChange = (idx, value, selectedOptions) => {
    if (!selectedOptions || selectedOptions.length === 0) return;
    const lastOption = selectedOptions[selectedOptions.length - 1];
    if (lastOption && lastOption.roll) {
      const r = lastOption.roll;
      const pn = rollNameList.find(n => n.id === r.product_name_id);
      const name = pn?.name || String(r.product_name_id) || '未知';
      // 获取第一级和第二级分类名称，拼接完整路径
      const level1 = selectedOptions[0]?.label || '';
      const level2 = selectedOptions[1]?.label || '';
      let fullName = name;
      if (level1 && level2) {
        fullName = `${level1}/${level2}/${name}`;
      } else if (level1) {
        fullName = `${level1}/${name}`;
      }
      const newLayers = [...costLayers];
      newLayers[idx].layer_name = fullName;
      newLayers[idx].gram = r.gram || 0;
      newLayers[idx].width = r.width || 0;
      setCostLayers(newLayers);
    }
  }

  // 确认成本测算，回填到明细行（保存所有详情以便回显）
  const confirmCostCalc = () => {
    const idx = costEditIdx;
    if (idx === null) return;
    updateItemRow(idx, 'actual_gram', costActualGram);
    updateItemRow(idx, 'cost', costPerPiece);
    updateItemRow(idx, 'waste_rate', costWasteRate);
    updateItemRow(idx, 'lamination_fee', costLaminationFee);
    updateItemRow(idx, 'cost_layers', JSON.stringify(costLayers));
    setCostModalOpen(false);
    // 提示信息
    const wasteLayers = costWasteInfo.filter(w => w.waste > 0);
    let wasteMsg = '';
    if (wasteLayers.length > 0) {
      wasteMsg = `，其中${wasteLayers.length}层有幅宽损耗（${wasteLayers.map(w => `第${w.idx+1}层多${w.waste}mm`).join('、')}）`;
    }
    let extraMsg = '';
    if (costWasteRate > 0) extraMsg += `，损耗率${costWasteRate}%`;
    if (costLaminationFee > 0) extraMsg += `，裱工费${costLaminationFee}元/吨`;
    message.success(`成本测算完成：实克${costActualGram}g，成本¥${costPerPiece.toFixed(4)}/张${wasteMsg}${extraMsg}`);
  }

  // 选择客户后自动带出信息
  const handleCustomerSelect = (customerId) => {
    const customer = customerList.find(c => c.id === customerId);
    if (customer) {
      editForm.setFieldsValue({
        customer_name: customer.customer_name,
        receiver: customer.contact || '',
        receiver_phone: customer.phone || '',
        delivery_address: customer.address || '',
        salesman: customer.salesman || '',
      });
    }
  }

  // 自动保存定时器
  const autoSaveTimer = useRef(null);
  const [autoSaving, setAutoSaving] = useState(false);
  const [lastSaveTime, setLastSaveTime] = useState(null);

  // 自动保存（防抖1.5秒）
  const triggerAutoSave = () => {
    if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
    setAutoSaving(true);
    autoSaveTimer.current = setTimeout(() => {
      doAutoSave();
    }, 1500);
  };

  // 执行自动保存
  const doAutoSave = async () => {
    if (!editingId) return;
    try {
      const values = editForm.getFieldsValue();
      const validItems = items.filter(it => it.product_name && String(it.product_name).trim());
      const payload = {
        customer_id: values.customer_id || null,
        customer_name: values.customer_name || '',
        customer_order_no: values.customer_order_no || null,
        receiver: values.receiver || null,
        receiver_phone: values.receiver_phone || null,
        delivery_address: values.delivery_address || null,
        delivery_date: values.delivery_date ? values.delivery_date.format('YYYY-MM-DD') : dayjs().format('YYYY-MM-DD'),
        status: values.status || 'draft',
        maker: values.maker || null,
        salesman: values.salesman || null,
        remark: values.remark || null,
        items: validItems.map((it, idx) => ({
          line_no: idx + 1,
          product_id: it.product_id || null,
          product_name: String(it.product_name || ''),
          spec: it.spec || null,
          length: Number(it.length) || 0,
          width: Number(it.width) || 0,
          nominal_gram: Number(it.nominal_gram) || 0,
          actual_gram: Number(it.actual_gram) || 0,
          unit: it.unit || '张',
          quantity: Number(it.quantity) || 0,
          ton_price: Number(it.ton_price) || 0,
          unit_price: Number(it.unit_price) || 0,
          amount: Number(it.amount) || 0,
          cost: Number(it.cost) || 0,
          waste_rate: Number(it.waste_rate) || 0,
          lamination_fee: Number(it.lamination_fee) || 0,
          cost_layers: it.cost_layers ? JSON.stringify(it.cost_layers) : null,
          remark: it.remark || null,
        })),
      };
      await api.put(`/api/sales_order/${editingId}`, payload);
      setLastSaveTime(new Date());
      setAutoSaving(false);
    } catch (err) {
      console.error("自动保存失败详情", JSON.stringify(err.response?.data, null, 2));
      setAutoSaving(false);
    }
  };

  // 打开新增（先创建草稿订单，再编辑）
  const openAdd = async () => {
    try {
      // 先创建一个空的草稿订单
      const res = await api.post("/api/sales_order", {
        customer_name: "（未命名草稿）",
        delivery_date: dayjs().format('YYYY-MM-DD'),
        status: "draft",
        items: [{
          line_no: 1,
          product_name: "",
          length: 0,
          width: 0,
          nominal_gram: 0,
          actual_gram: 0,
          unit: "张",
          quantity: 0,
          ton_price: 0,
          unit_price: 0,
          amount: 0,
          cost: 0,
          waste_rate: 3,
          lamination_fee: 300,
          cost_layers: "",
          remark: ""
        }]
      });
      setEditingId(res.data.id);
      editForm.resetFields();
      editForm.setFieldsValue({
        customer_name: "",
        delivery_date: dayjs(),
        status: 'draft',
      });
      setItems([createEmptyItem(1)]);
      setEditModalOpen(true);
      message.info("已创建草稿，修改将自动保存");
    } catch (err) {
      message.error("创建草稿失败：" + (err.response?.data?.detail || err.message));
    }
  }

  // 打开编辑
  const openEdit = async (record) => {
    setEditingId(record.id);
    try {
      const res = await api.get(`/api/sales_order/${record.id}`);
      const order = res.data;
      editForm.setFieldsValue({
        customer_id: order.customer_id,
        customer_name: order.customer_name,
        customer_order_no: order.customer_order_no || '',
        receiver: order.receiver || '',
        receiver_phone: order.receiver_phone || '',
        delivery_address: order.delivery_address || '',
        delivery_date: order.delivery_date ? dayjs(order.delivery_date) : dayjs(),
        status: order.status,
        maker: order.maker || '',
        salesman: order.salesman || '',
        remark: order.remark || '',
      });
      if (order.items && order.items.length > 0) {
        setItems(order.items.map(it => ({
          line_no: it.line_no,
          product_name: it.product_name || '',
          spec: it.spec || '',
          length: it.length || 0,
          width: it.width || 0,
          nominal_gram: it.nominal_gram || 0,
          actual_gram: it.actual_gram || 0,
          unit: it.unit || '张',
          quantity: it.quantity || 0,
          ton_price: it.ton_price || 0,
          unit_price: it.unit_price || 0,
          amount: it.amount || 0,
          cost: it.cost || 0,
          waste_rate: it.waste_rate !== undefined && it.waste_rate !== null ? it.waste_rate : 3,
          lamination_fee: it.lamination_fee !== undefined && it.lamination_fee !== null ? it.lamination_fee : 300,
          cost_layers: it.cost_layers ? JSON.stringify(it.cost_layers) : '',
          remark: it.remark || '',
        })));
      } else {
        setItems([createEmptyItem(1)]);
      }
      setEditModalOpen(true);
    } catch (err) {
      message.error("加载订单详情失败");
    }
  }

  // 保存
  const handleSave = async () => {
    try {
      const values = await editForm.validateFields();
      if (!values.customer_name || !values.customer_name.trim()) {
        message.error("请输入客户名称");
        return;
      }
      const validItems = items.filter(it => it.product_name && String(it.product_name).trim());
      if (validItems.length === 0) {
        message.error("请至少填写一行货品名称");
        return;
      }
      // 如果有未完成的自动保存，先执行
      if (autoSaveTimer.current) {
        clearTimeout(autoSaveTimer.current);
        await doAutoSave();
      }
      const payload = {
        customer_id: values.customer_id || null,
        customer_name: values.customer_name,
        customer_order_no: values.customer_order_no || null,
        receiver: values.receiver || null,
        receiver_phone: values.receiver_phone || null,
        delivery_address: values.delivery_address || null,
        delivery_date: values.delivery_date.format('YYYY-MM-DD'),
        status: values.status || 'pending',
        maker: values.maker || null,
        salesman: values.salesman || null,
        remark: values.remark || null,
        items: validItems.map((it, idx) => ({
          line_no: idx + 1,
          product_id: it.product_id || null,
          product_name: String(it.product_name || ''),
          spec: it.spec || null,
          length: Number(it.length) || 0,
          width: Number(it.width) || 0,
          nominal_gram: Number(it.nominal_gram) || 0,
          actual_gram: Number(it.actual_gram) || 0,
          unit: it.unit || '张',
          quantity: Number(it.quantity) || 0,
          ton_price: Number(it.ton_price) || 0,
          unit_price: Number(it.unit_price) || 0,
          amount: Number(it.amount) || 0,
          cost: Number(it.cost) || 0,
          waste_rate: Number(it.waste_rate) || 0,
          lamination_fee: Number(it.lamination_fee) || 0,
          cost_layers: it.cost_layers ? JSON.stringify(it.cost_layers) : null,
          remark: it.remark || null,
        })),
      };
      if (editingId) {
        await api.put(`/api/sales_order/${editingId}`, payload);
        message.success("保存成功");
      } else {
        await api.post("/api/sales_order", payload);
        message.success("新增成功");
      }
      setEditModalOpen(false);
      loadData();
    } catch (err) {
      if (err.errorFields) return;
      message.error(err.response?.data?.detail || err.message || "保存失败"); console.error("保存错误详情", JSON.stringify(err.response?.data, null, 2));
    }
  }

  // 删除
  const handleDelete = async (id) => {
    try {
      await api.delete(`/api/sales_order/${id}`);
      message.success("删除成功");
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "删除失败");
    }
  }

  // 修改订单状态
  const handleChangeStatus = async (record, newStatus) => {
    try {
      await api.put(`/api/sales_order/${record.id}`, { status: newStatus });
      message.success("状态修改成功");
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "状态修改失败");
    }
  }

  // 打开待出库订单弹窗
  const openPendingModal = async () => {
    setPendingModalOpen(true);
    try {
      const res = await api.get("/api/sales_order", { params: { status: "pending" } });
      setPendingList(res.data);
    } catch (err) {
      message.error("加载待出库订单失败");
    }
  }

  // 确认出库
  const handleShip = async (record) => {
    try {
      await api.post(`/api/sales_order/${record.id}/ship`);
      message.success("出库成功，已扣减成品库存，订单状态改为已送出");
      // 刷新待出库列表
      const res = await api.get("/api/sales_order", { params: { status: "pending" } });
      setPendingList(res.data);
      loadData();
    } catch (err) {
      message.error(err.response?.data?.detail || "出库失败");
    }
  }

  // 打印
  const handlePrint = async (record) => {
    try {
      const res = await api.get(`/api/sales_order/${record.id}`);
      setPrintData(res.data);
      setPrintOpen(true);
    } catch (err) {
      message.error("加载订单详情失败");
    }
  }

  // 表格列
  const columns = [
    { title: "订单编号", dataIndex: "order_no", key: "order_no", width: 180, fixed: 'left', render: v => <b>{v}</b> },
    { title: "客户名称", dataIndex: "customer_name", key: "customer_name", width: 180 },
    { title: "收货人", dataIndex: "receiver", key: "receiver", width: 100 },
    { title: "送货日期", dataIndex: "delivery_date", key: "delivery_date", width: 110 },
    {
      title: "明细", key: "items", width: 220,
      render: (_, record) => (
        <div>
          {record.items && record.items.slice(0, 2).map((it, i) => (
            <div key={i} style={{ fontSize: 12 }}>{it.product_name} {it.spec || ''} × {it.quantity}{it.unit}</div>
          ))}
          {record.items && record.items.length > 2 && <div style={{ fontSize: 12, color: '#999' }}>...共{record.items.length}项</div>}
        </div>
      )
    },
    {
      title: "合计金额", dataIndex: "total_amount", key: "total_amount", width: 110,
      render: v => <b style={{ color: '#cf1322' }}>¥{Number(v).toFixed(2)}</b>
    },
    {
      title: "状态", dataIndex: "status", key: "status", width: 90,
      render: v => {
        const s = STATUS_MAP[v] || { label: v, color: 'default' };
        return <Tag color={s.color}>{s.label}</Tag>;
      }
    },
    { title: "业务员", dataIndex: "salesman", key: "salesman", width: 90 },
    {
      title: "操作", key: "action", width: 360, fixed: 'right',
      render: (_, record) => (
        <Space wrap size={4}>
          <Button size="small" type="primary" onClick={() => handlePrint(record)}>打印</Button>
          <Button 
            size="small" 
            type={record.status === "draft" ? "primary" : "default"}
            onClick={() => {
              if (record.status === "draft") return;
              Modal.confirm({
                title: "确认打回草稿？",
                content: "打回草稿后，所有待出库库存都会加回。",
                onOk: () => handleChangeStatus(record, "draft")
              });
            }}
          >草稿</Button>
          <Button 
            size="small" 
            type={record.status === "pending" ? "primary" : "default"}
            onClick={() => {
              if (record.status === "pending") return;
              Modal.confirm({
                title: "确认切换为待出库？",
                content: "切换为待出库后，系统会自动在成品仓锁定对应库存。",
                onOk: () => handleChangeStatus(record, "pending")
              });
            }}
          >待出库</Button>
          <Button 
            size="small" 
            type={record.status === "shipped" ? "primary" : "default"}
            onClick={() => {
              if (record.status === "shipped") return;
              Modal.confirm({
                title: "确认标记为已出库？",
                content: "确认后将真正扣减成品仓总库存，不可恢复。",
                onOk: () => handleChangeStatus(record, "shipped")
              });
            }}
          >已出库</Button>
          <Button 
            size="small" 
            type={record.status === "completed" ? "primary" : "default"}
            onClick={() => {
              if (record.status === "completed") return;
              Modal.confirm({
                title: "确认标记为已完成？",
                content: "确认表示客户已实际收货。",
                onOk: () => handleChangeStatus(record, "completed")
              });
            }}
          >已完成</Button>
          <Button 
            size="small" 
            danger={record.status === "cancelled"}
            onClick={() => {
              if (record.status === "cancelled") return;
              Modal.confirm({
                title: "确认取消订单？",
                content: "取消订单后，所有待出库库存都会加回。",
                onOk: () => handleChangeStatus(record, "cancelled")
              });
            }}
          >取消</Button>
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除该订单？" onConfirm={() => handleDelete(record.id)} okText="确认" cancelText="取消">
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  // 成品库选择表格列
  const productSelectColumns = [
    { title: '品名', dataIndex: 'product_name_id', key: 'name', render: (v) => pnList.find(p => p.id === v)?.name || v || '-' },
    { title: '规格', dataIndex: 'spec', key: 'spec' },
    { title: '实克', dataIndex: 'actual_gram', key: 'actual_gram' },
    { title: '虚克', dataIndex: 'nominal_gram', key: 'nominal_gram' },
    { title: '单位', dataIndex: 'unit', key: 'unit' },
    { title: '可用库存', dataIndex: 'quantity', key: 'quantity' },
    {
      title: '操作', key: 'action',
      render: (_, record) => (
        <Button size="small" type="primary" onClick={() => handleSelectProduct(record)}>选择</Button>
      )
    }
  ];

  return (
    <div style={{ padding: 20 }}>
      <h2 style={{ marginBottom: 16 }}>销售订单（送货单）</h2>

      {/* 搜索栏 */}
      <div style={{ marginBottom: 16, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <Button type="primary" onClick={openAdd}>新增订单</Button>
        <Button onClick={openPendingModal}>待出库订单</Button>
        <Input
          placeholder="搜索客户名称"
          value={searchCustomer}
          onChange={e => setSearchCustomer(e.target.value)}
          style={{ width: 200 }}
          allowClear
        />
        <Select
          placeholder="按客户筛选"
          value={searchCustomerId || undefined}
          onChange={val => setSearchCustomerId(val)}
          style={{ width: 180 }}
          allowClear
        >
          {customerList.map(c => <Select.Option key={c.id} value={c.id}>{c.customer_name}</Select.Option>)}
        </Select>
        <Select
          placeholder="订单状态"
          value={searchStatus}
          onChange={val => setSearchStatus(val)}
          style={{ width: 130 }}
          allowClear
        >
          {Object.entries(STATUS_MAP).map(([k, v]) => (
            <Select.Option key={k} value={k}>{v.label}</Select.Option>
          ))}
        </Select>
        <DatePicker.RangePicker
          value={searchDateRange}
          onChange={val => setSearchDateRange(val)}
          placeholder={['开始日期', '结束日期']}
        />
        <Select
          placeholder="筛选字段"
          value={searchField || undefined}
          onChange={val => setSearchField(val)}
          style={{ width: 120 }}
          allowClear
        >
          <Select.Option value="order_no">订单编号</Select.Option>
          <Select.Option value="customer_name">客户名称</Select.Option>
          <Select.Option value="salesman">业务员</Select.Option>
          <Select.Option value="receiver">收货人</Select.Option>
          <Select.Option value="delivery_date">送货日期</Select.Option>
          <Select.Option value="status">订单状态</Select.Option>
        </Select>
        <Input
          placeholder="输入筛选值"
          value={searchValue}
          onChange={e => setSearchValue(e.target.value)}
          style={{ width: 160 }}
          allowClear
          onPressEnter={loadData}
        />
        <Button onClick={loadData}>搜索</Button>
      </div>

      {/* 订单表格 */}
      <Table
        rowKey="id"
        dataSource={orderList}
        columns={columns}
        loading={loading}
        bordered
        scroll={{ x: 'max-content' }}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
          showTotal: t => `共 ${t} 条`
        }}
      />

      {/* 新增/编辑弹窗 */}
      <Modal
        open={editModalOpen}
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span>{editingId ? "编辑销售订单" : "新增销售订单"}</span>
            {editingId && (
              <span style={{ fontSize: 12, fontWeight: 400, color: autoSaving ? '#fa8c16' : '#52c41a' }}>
                {autoSaving ? '保存中...' : lastSaveTime ? `已自动保存 ${lastSaveTime.toLocaleTimeString()}` : '自动保存已开启'}
              </span>
            )}
          </div>
        }
        onCancel={() => setEditModalOpen(false)}
        onOk={handleSave}
        width={1200}
        destroyOnClose
      >
        <Form form={editForm} layout="vertical" onValuesChange={() => { if (editingId) triggerAutoSave(); }}>
          {/* 客户信息 */}
          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item label="选择客户（自动带出信息）" name="customer_id" style={{ flex: 1 }}>
              <Select
                placeholder="从客户档案选择"
                showSearch
                optionFilterProp="label"
                allowClear
                onChange={handleCustomerSelect}
                options={customerList.map(c => ({
                  value: c.id,
                  label: `${c.customer_name}（${c.contact || ''}）`
                }))}
              />
            </Form.Item>
            <Form.Item label="客户名称" name="customer_name" style={{ flex: 1 }} rules={[{ required: true, message: "请输入客户名称" }]}>
              <Input placeholder="客户名称" />
            </Form.Item>
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item label="客户订单号" name="customer_order_no" style={{ flex: 1 }}>
              <Input placeholder="客户自己的订单号（可选）" />
            </Form.Item>
            <Form.Item label="送货日期" name="delivery_date" style={{ flex: 1 }} rules={[{ required: true, message: "请选择送货日期" }]}>
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item label="收货人" name="receiver" style={{ flex: 1 }}>
              <Input placeholder="收货人姓名" />
            </Form.Item>
            <Form.Item label="收货人电话" name="receiver_phone" style={{ flex: 1 }}>
              <Input placeholder="收货人电话" />
            </Form.Item>
          </div>

          <Form.Item label="送货地址" name="delivery_address">
            <Input placeholder="送货地址" />
          </Form.Item>

          <div style={{ display: 'flex', gap: 12 }}>
            <Form.Item label="业务员" name="salesman" style={{ flex: 1 }}>
              <Input placeholder="业务员" />
            </Form.Item>
            <Form.Item label="制单人" name="maker" style={{ flex: 1 }}>
              <Input placeholder="制单人" />
            </Form.Item>
            <Form.Item label="订单状态" name="status" style={{ flex: 1 }}>
              <Select>
                {Object.entries(STATUS_MAP).map(([k, v]) => (
                  <Select.Option key={k} value={k}>{v.label}</Select.Option>
                ))}
              </Select>
            </Form.Item>
          </div>

          <Divider orientation="left" style={{ fontSize: 14 }}>订单明细（输入长宽/虚克/吨价自动算单价，点成本测算算实克和成本）</Divider>

          {/* 明细表格 - 横向滚动 */}
          <div style={{ border: '1px solid #f0f0f0', borderRadius: 4, marginBottom: 8, overflowX: 'auto' }}>
            <div style={{ minWidth: 1400 }}>
              <div style={{ display: 'flex', background: '#fafafa', padding: '8px 4px', borderBottom: '1px solid #f0f0f0', fontWeight: 600, fontSize: 13 }}>
                <div style={{ width: 40, textAlign: 'center', flexShrink: 0 }}>行号</div>
                <div style={{ width: 70, textAlign: 'center', flexShrink: 0 }}>选成品</div>
                <div style={{ width: 140, padding: '0 4px', flexShrink: 0 }}>货品名称</div>
                <div style={{ width: 70, padding: '0 4px', flexShrink: 0 }}>宽(mm)</div>
                <div style={{ width: 70, padding: '0 4px', flexShrink: 0 }}>长(mm)</div>
                <div style={{ width: 70, padding: '0 4px', flexShrink: 0 }}>虚克(g)</div>
                <div style={{ width: 70, padding: '0 4px', flexShrink: 0 }}>实克(g)</div>
                <div style={{ width: 60, padding: '0 4px', flexShrink: 0 }}>单位</div>
                <div style={{ width: 70, padding: '0 4px', flexShrink: 0 }}>数量</div>
                <div style={{ width: 80, padding: '0 4px', flexShrink: 0 }}>吨价(元)</div>
                <div style={{ width: 80, padding: '0 4px', flexShrink: 0 }}>单价(元)</div>
                <div style={{ width: 90, padding: '0 4px', flexShrink: 0 }}>金额(元)</div>
                <div style={{ width: 110, padding: '0 4px', flexShrink: 0 }}>成本(实克/虚克×成本)</div>
                <div style={{ width: 90, textAlign: 'center', flexShrink: 0 }}>成本测算</div>
                <div style={{ flex: 1, padding: '0 4px', minWidth: 80 }}>备注</div>
                <div style={{ width: 50, textAlign: 'center', flexShrink: 0 }}>操作</div>
              </div>
              {items.map((it, idx) => (
                <div key={idx} style={{ display: 'flex', padding: '4px', borderBottom: idx < items.length - 1 ? '1px solid #f5f5f5' : 'none', alignItems: 'center' }}>
                  <div style={{ width: 40, textAlign: 'center', color: '#999', flexShrink: 0 }}>{idx + 1}</div>
                  <div style={{ width: 70, textAlign: 'center', flexShrink: 0 }}>
                    <Button size="small" onClick={() => openProductSelect(idx)}>选成品</Button>
                  </div>
                  <div style={{ width: 140, padding: '0 2px', flexShrink: 0 }}>
                    <AutoComplete
                      value={it.product_name}
                      onChange={val => handleProductSelect(idx, val)}
                      options={productNameOptions}
                      placeholder="货品名称"
                      size="small"
                      style={{ width: '100%' }}
                    />
                  </div>
                  <div style={{ width: 70, padding: '0 2px', flexShrink: 0 }}>
                    <InputNumber size="small" min={0} value={it.width} onChange={val => updateItemRow(idx, 'width', val)} style={{ width: '100%' }} placeholder="宽" />
                  </div>
                  <div style={{ width: 70, padding: '0 2px', flexShrink: 0 }}>
                    <InputNumber size="small" min={0} value={it.length} onChange={val => updateItemRow(idx, 'length', val)} style={{ width: '100%' }} placeholder="长" />
                  </div>
                  <div style={{ width: 70, padding: '0 2px', flexShrink: 0 }}>
                    <InputNumber size="small" min={0} value={it.nominal_gram} onChange={val => updateItemRow(idx, 'nominal_gram', val)} style={{ width: '100%' }} placeholder="虚克" />
                  </div>
                  <div style={{ width: 70, padding: '0 2px', flexShrink: 0, color: it.actual_gram ? '#1677ff' : '#999', fontWeight: it.actual_gram ? 600 : 400 }}>
                    {it.actual_gram ? it.actual_gram : '-'}
                  </div>
                  <div style={{ width: 60, padding: '0 2px', flexShrink: 0 }}>
                    <Input size="small" value={it.unit} onChange={e => updateItemRow(idx, 'unit', e.target.value)} placeholder="张" />
                  </div>
                  <div style={{ width: 70, padding: '0 2px', flexShrink: 0 }}>
                    <InputNumber 
                      size="small" 
                      min={0} 
                      value={it.quantity} 
                      onChange={val => updateItemRow(idx, 'quantity', val)} 
                      style={{ 
                        width: '100%',
                        borderColor: (() => {
                          if (!it.product_id) return undefined;
                          const p = productList.find(x => x.id === it.product_id);
                          if (!p) return undefined;
                          const available = (p.quantity || 0) - (p.pending_out_qty || 0);
                          return (Number(it.quantity) || 0) > available ? '#ff4d4f' : undefined;
                        })(),
                        boxShadow: (() => {
                          if (!it.product_id) return undefined;
                          const p = productList.find(x => x.id === it.product_id);
                          if (!p) return undefined;
                          const available = (p.quantity || 0) - (p.pending_out_qty || 0);
                          return (Number(it.quantity) || 0) > available ? '0 0 0 2px rgba(255,77,79,0.2)' : undefined;
                        })()
                      }} 
                      placeholder="数量" 
                    />
                    {(() => {
                      if (!it.product_id) return null;
                      const p = productList.find(x => x.id === it.product_id);
                      if (!p) return null;
                      const available = (p.quantity || 0) - (p.pending_out_qty || 0);
                      const qty = Number(it.quantity) || 0;
                      if (qty > available) {
                        return <div style={{ fontSize: 10, color: '#ff4d4f', marginTop: 2 }}>库存不足！可用: {available}</div>;
                      }
                      return null;
                    })()}
                  </div>
                  <div style={{ width: 80, padding: '0 2px', flexShrink: 0 }}>
                    <InputNumber size="small" min={0} step="1" value={it.ton_price} onChange={val => updateItemRow(idx, 'ton_price', val)} style={{ width: '100%' }} placeholder="吨价" />
                  </div>
                  <div style={{ width: 80, padding: '0 2px', flexShrink: 0, color: '#1677ff', fontWeight: 600, fontSize: 12 }}>
                    ¥{Number(it.unit_price).toFixed(4)}
                  </div>
                  <div style={{ width: 90, padding: '0 2px', flexShrink: 0, textAlign: 'right', color: '#cf1322', fontWeight: 600 }}>
                    ¥{Number(it.amount).toFixed(2)}
                  </div>
                  <div style={{ width: 110, padding: '0 2px', flexShrink: 0, fontSize: 11, lineHeight: 1.4 }}>
                    {Number(it.cost) > 0 && Number(it.nominal_gram) > 0 ? (
                      <div>
                        <div style={{ color: '#52c41a', fontWeight: 600 }}>
                          ¥{(Number(it.actual_gram) / Number(it.nominal_gram) * Number(it.cost)).toFixed(4)}/张
                        </div>
                        <div style={{ color: '#fa8c16' }}>
                          ¥{Number(it.length) > 0 && Number(it.width) > 0 && Number(it.nominal_gram) > 0
                            ? (Number(it.cost) / (Number(it.length) * Number(it.width) / 1000000) / Number(it.nominal_gram) * 1000000).toFixed(0)
                            : 0}/吨
                        </div>
                      </div>
                    ) : <span style={{ color: '#999' }}>-</span>}
                  </div>
                  <div style={{ width: 90, textAlign: 'center', flexShrink: 0 }}>
                    <Button size="small" type={it.cost ? 'default' : 'primary'} onClick={() => openCostCalc(idx)}>
                      {it.cost ? '修改' : '成本测算'}
                    </Button>
                  </div>
                  <div style={{ flex: 1, padding: '0 2px', minWidth: 80 }}>
                    <Input size="small" value={it.remark} onChange={e => updateItemRow(idx, 'remark', e.target.value)} />
                  </div>
                  <div style={{ width: 50, textAlign: 'center', flexShrink: 0 }}>
                    <Button size="small" type="link" danger onClick={() => removeItemRow(idx)}>删除</Button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <Button type="dashed" onClick={addItemRow} style={{ width: 120 }}>+ 添加一行</Button>
            <div style={{ fontSize: 16, fontWeight: 600 }}>
              合计金额：<span style={{ color: '#cf1322' }}>¥{totalAmount.toFixed(2)}</span>
              <span style={{ fontSize: 12, color: '#999', marginLeft: 12 }}>大写：{amountToChinese(totalAmount)}</span>
            </div>
          </div>

          <Form.Item name="tax_included" valuePropName="checked">
            <Checkbox>不含税（打钩表示不含税）</Checkbox>
          </Form.Item>

          <Form.Item label="备注" name="remark">
            <Input.TextArea rows={2} placeholder="订单备注（可选）" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 成本测算弹窗 */}
      <Modal
        open={costModalOpen}
        title="成本测算（最多5裱，级联选择卷筒仓库存，自动带出克重/幅宽；幅宽大于成品宽的部分自动算入损耗）"
        onCancel={() => setCostModalOpen(false)}
        width={1100}
        zIndex={2500}
        footer={
          <Space>
            <Button onClick={() => setCostModalOpen(false)}>取消</Button>
            <Button type="primary" onClick={confirmCostCalc}>确认并回填</Button>
          </Space>
        }
      >
        <div style={{ marginBottom: 12, padding: '8px 12px', background: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: 4, fontSize: 13 }}>
          <b>计算说明：</b>纸名可从卷筒仓库存选择（自动带出克重/幅宽）；每层成本按实际幅宽计算，若某层幅宽大于成品宽，多出部分自动算入损耗成本；可额外设置损耗率(%)和裱工费(元/吨)；实克 = 各层克重之和
        </div>

        {/* 成本层表格 */}
        <div style={{ border: '1px solid #f0f0f0', borderRadius: 4, marginBottom: 12 }}>
          <div style={{ display: 'flex', background: '#fafafa', padding: '8px 4px', borderBottom: '1px solid #f0f0f0', fontWeight: 600, fontSize: 13 }}>
            <div style={{ width: 50, textAlign: 'center' }}>层号</div>
            <div style={{ flex: 1.5, padding: '0 4px' }}>选卷筒(级联)</div>
            <div style={{ flex: 1.2, padding: '0 4px' }}>纸名</div>
            <div style={{ width: 80, padding: '0 4px' }}>克重(g)</div>
            <div style={{ width: 80, padding: '0 4px' }}>幅宽(mm)</div>
            <div style={{ width: 70, padding: '0 4px', textAlign: 'center' }}>损耗(mm)</div>
            <div style={{ width: 100, padding: '0 4px' }}>吨价(元/吨)</div>
            <div style={{ width: 110, padding: '0 4px', textAlign: 'right' }}>该层成本(元/张)</div>
            <div style={{ width: 50, textAlign: 'center' }}>操作</div>
          </div>
          {costLayers.map((layer, idx) => {
            const wasteInfo = costWasteInfo[idx] || { waste: 0 };
            const productLength = costEditIdx !== null && items[costEditIdx] ? Number(items[costEditIdx].length) || 0 : 0;
            const layerCost = productLength * (Number(layer.width) || 0) * (Number(layer.gram) || 0) * (Number(layer.ton_price) || 0) / 1e12;
            return (
            <div key={idx} style={{ display: 'flex', padding: '4px', borderBottom: idx < costLayers.length - 1 ? '1px solid #f5f5f5' : 'none', alignItems: 'center' }}>
              <div style={{ width: 50, textAlign: 'center', color: '#999' }}>第{idx + 1}层</div>
              <div style={{ flex: 1.5, padding: '0 2px' }}>
                <Cascader
                  size="small"
                  options={rollCascaderOptions}
                  onChange={(value, selectedOptions) => handleRollCascaderChange(idx, value, selectedOptions)}
                  placeholder="点选卷筒"
                  style={{ width: '100%' }}
                  displayRender={({ labels }) => (labels || []).join(' / ')}
                />
              </div>
              <div style={{ flex: 1.2, padding: '0 2px' }}>
                <Input size="small" value={layer.layer_name} onChange={e => updateCostLayer(idx, 'layer_name', e.target.value)} placeholder="纸名" />
              </div>
              <div style={{ width: 80, padding: '0 2px' }}>
                <InputNumber size="small" min={0} value={layer.gram} onChange={val => updateCostLayer(idx, 'gram', val)} style={{ width: '100%' }} placeholder="350" />
              </div>
              <div style={{ width: 80, padding: '0 2px' }}>
                <InputNumber size="small" min={0} value={layer.width} onChange={val => updateCostLayer(idx, 'width', val)} style={{ width: '100%' }} placeholder="787" />
              </div>
              <div style={{ width: 70, padding: '0 2px', textAlign: 'center', color: wasteInfo.waste > 0 ? '#fa8c16' : '#999', fontSize: 12, fontWeight: wasteInfo.waste > 0 ? 600 : 400 }}>
                {wasteInfo.waste > 0 ? `+${wasteInfo.waste}` : '-'}
              </div>
              <div style={{ width: 100, padding: '0 2px' }}>
                <InputNumber size="small" min={0} step="1" value={layer.ton_price} onChange={val => updateCostLayer(idx, 'ton_price', val)} style={{ width: '100%' }} placeholder="2270" />
              </div>
              <div style={{ width: 110, padding: '0 2px', textAlign: 'right', color: '#1677ff', fontWeight: 600, fontSize: 12 }}>
                ¥{layerCost.toFixed(4)}
              </div>
              <div style={{ width: 50, textAlign: 'center' }}>
                <Button size="small" type="link" danger onClick={() => removeCostLayer(idx)}>删除</Button>
              </div>
            </div>
            );
          })}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
          <div>
            <Button type="dashed" onClick={addCostLayer} disabled={costLayers.length >= 5}>+ 添加一层（最多5层）</Button>
            <div style={{ marginTop: 12, display: 'flex', gap: 16, alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: 12, color: '#666', marginRight: 6 }}>损耗率(%)</span>
                <InputNumber size="small" min={0} step="0.1" value={costWasteRate} onChange={val => setCostWasteRate(val || 0)} style={{ width: 90 }} placeholder="5" />
              </div>
              <div>
                <span style={{ fontSize: 12, color: '#666', marginRight: 6 }}>裱工费(元/吨)</span>
                <InputNumber size="small" min={0} step="1" value={costLaminationFee} onChange={val => setCostLaminationFee(val || 0)} style={{ width: 90 }} placeholder="200" />
              </div>
            </div>
          </div>
          <div style={{ fontSize: 15, fontWeight: 600, lineHeight: 1.8, textAlign: 'right' }}>
            <div>实克合计：<span style={{ color: '#1677ff' }}>{costActualGram} g/m²</span></div>
            {costEditIdx !== null && items[costEditIdx] && (
              <>
                <div>成品尺寸：{items[costEditIdx].length}×{items[costEditIdx].width}mm</div>
                <div>实克成本（张价）：
                  <span style={{ color: '#52c41a' }}>¥{costPerPiece.toFixed(4)} /张</span>
                </div>
                {Number(items[costEditIdx].nominal_gram) > 0 && costActualGram > 0 && (
                  <div>虚克成本（张价）：
                    <span style={{ color: '#fa8c16' }}>¥{(costPerPiece * Number(items[costEditIdx].nominal_gram) / costActualGram).toFixed(4)} /张</span>
                  </div>
                )}
                {Number(items[costEditIdx].length) > 0 && Number(items[costEditIdx].width) > 0 && costActualGram > 0 && (
                  <div>实克成本（吨价）：
                    <span style={{ color: '#52c41a' }}>¥{(costPerPiece / (Number(items[costEditIdx].length) * Number(items[costEditIdx].width) / 1000000) / costActualGram * 1000000).toFixed(0)} /吨</span>
                  </div>
                )}
                {Number(items[costEditIdx].length) > 0 && Number(items[costEditIdx].width) > 0 && Number(items[costEditIdx].nominal_gram) > 0 && costActualGram > 0 && (
                  <div>虚克成本（吨价）：
                    <span style={{ color: '#fa8c16' }}>¥{(costPerPiece / (Number(items[costEditIdx].length) * Number(items[costEditIdx].width) / 1000000) / Number(items[costEditIdx].nominal_gram) * 1000000).toFixed(0)} /吨</span>
                  </div>
                )}
                {costWasteInfo.filter(w => w.waste > 0).length > 0 && (
                  <div style={{ fontSize: 12, color: '#fa8c16' }}>
                    幅宽损耗：{costWasteInfo.filter(w => w.waste > 0).map(w => `第${w.idx+1}层多${w.waste}mm`).join('、')}
                  </div>
                )}
                {costWasteRate > 0 && (
                  <div style={{ fontSize: 12, color: '#fa8c16' }}>
                    损耗率：{costWasteRate}%
                  </div>
                )}
                {costLaminationFee > 0 && (
                  <div style={{ fontSize: 12, color: '#1890ff' }}>
                    裱工费：{costLaminationFee}元/吨
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        <div style={{ padding: '8px 12px', background: '#e6f7ff', border: '1px solid #91d5ff', borderRadius: 4, fontSize: 13 }}>
          <b>示例：</b>金盾350g 787 吨价2270 + 银盾500g 787 吨价1960 + 铜版纸90g 787 吨价4500 → 实克940g，可当1100g卖
        </div>
      </Modal>

      {/* 选择成品弹窗 */}
      <Modal
        open={productModalOpen}
        title="从成品库选择成品"
        onCancel={() => setProductModalOpen(false)}
        width={900}
        zIndex={2000}
        footer={null}
      >
        <Table
          rowKey="id"
          dataSource={productList}
          columns={productSelectColumns}
          size="small"
          pagination={{ pageSize: 10 }}
        />
      </Modal>

      {/* 待出库订单弹窗 */}
      <Modal
        open={pendingModalOpen}
        title="待出库订单"
        onCancel={() => setPendingModalOpen(false)}
        footer={
          <Space>
            <Button danger onClick={async () => {
              if (pickListOrders.length === 0) { message.warning("请先勾选要出库的订单"); return; }
              if (!window.confirm(`确定要对选中的 ${pickListOrders.length} 个订单批量确认出库吗？`)) return;
              setShipLoading(true);
              try {
                for (const order of pickListOrders) {
                  await api.post(`/api/sales_order/${order.id}/ship`);
                }
                message.success("批量出库成功");
                setPickListOrders([]);
                loadData();
              } catch (e) {
                message.error("批量出库失败：" + (e.response?.data?.detail || e.message));
              } finally {
                setShipLoading(false);
              }
            }} loading={shipLoading}>
              批量确认出库（{pickListOrders.length}个）
            </Button>
            <Button type="primary" onClick={() => { if (pickListOrders.length === 0) { message.warning("请先勾选要打印的订单"); return; } setShowPickListPrint(true); }}>
              打印选中备货单（{pickListOrders.length}个）
            </Button>
            <Button onClick={() => setPendingModalOpen(false)}>关闭</Button>
          </Space>
        }
        width={1000}
        zIndex={2000}
      >
        <Table
          rowKey="id"
          dataSource={pendingList}
          rowSelection={{
            selectedRowKeys: pickListOrders.map(o => o.id),
            onChange: (keys, rows) => setPickListOrders(rows)
          }}
          columns={[
            { title: "订单编号", dataIndex: "order_no", width: 150 },
            { title: "客户名称", dataIndex: "customer_name", width: 150 },
            { title: "送货日期", dataIndex: "delivery_date", width: 110 },
            { title: "明细", key: "items", render: (_, r) => (
              <div>
                {r.items && r.items.slice(0, 2).map((it, i) => {
                  // 检查库存是否不足
                  let isWarn = false;
                  if (it.product_id) {
                    const p = productList.find(x => x.id === it.product_id);
                    if (p) {
                      const available = (p.quantity || 0) - (p.pending_out_qty || 0);
                      isWarn = (Number(it.quantity) || 0) > available;
                    }
                  }
                  return (
                    <div key={i} style={{ fontSize: 12, color: isWarn ? '#ff4d4f' : undefined, fontWeight: isWarn ? 600 : 400 }}>
                      {it.product_name} {it.spec || ""} × {it.quantity}{it.unit}
                      {isWarn && <span style={{ fontSize: 10 }}> (库存不足!)</span>}
                    </div>
                  );
                })}
              </div>
            )},
            { title: "合计金额", dataIndex: "total_amount", width: 110, render: v => <b style={{ color: "#cf1322" }}>¥{Number(v).toFixed(2)}</b> },
            { title: "操作", key: "action", width: 180, render: (_, record) => (
              <Space wrap>
                <Button size="small" type="primary" onClick={() => handleShip(record)}>确认出库</Button>
                <Button size="small" onClick={() => { setPendingModalOpen(false); openEdit(record); }}>编辑</Button>
              </Space>
            )}
          ]}
          pagination={false}
          size="small"
        />
      </Modal>

      {/* 备货单打印弹窗 */}
      <StockPickListPrint orders={pickListOrders} open={showPickListPrint} onCancel={() => setShowPickListPrint(false)} />

      {/* 打印弹窗 */}
      <Modal
        open={printOpen}
        title="打印预览 - 送货单"
        onCancel={() => setPrintOpen(false)}
        zIndex={3000}
        footer={
          <Space>
            <Button onClick={() => setPrintOpen(false)}>关闭</Button>
            <Button type="primary" onClick={() => window.print()}>打印</Button>
          </Space>
        }
        width={1000}
      >
        {printData && <SalesOrderPrint order={printData} />}
      </Modal>
    </div>
  );
}
