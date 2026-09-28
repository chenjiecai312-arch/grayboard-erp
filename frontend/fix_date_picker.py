with open('src/ProduceOrder.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 导入 dayjs
content = content.replace(
    "import React, { useState, useEffect } from 'react';",
    "import React, { useState, useEffect } from 'react';\nimport dayjs from 'dayjs';"
)

# 2. openEdit 里 produce_date 转成 dayjs
content = content.replace(
    "      produce_date: record.produce_date,",
    "      produce_date: record.produce_date ? dayjs(record.produce_date) : null,"
)

# 3. handleSave 里 produce_date 转成字符串
content = content.replace(
    '''      const payload = {
        ...values,
        customer_name: customer?.customer_name || values.customer_name,''',
    '''      const payload = {
        ...values,
        produce_date: values.produce_date ? values.produce_date.format('YYYY-MM-DD') : null,
        customer_name: customer?.customer_name || values.customer_name,'''
)

with open('src/ProduceOrder.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('日期格式问题修复完成')
