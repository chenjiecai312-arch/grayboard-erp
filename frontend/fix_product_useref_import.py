with open('src/ProductWarehouse.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "import React, { useState, useEffect, useMemo } from 'react';",
    "import React, { useState, useEffect, useMemo, useRef } from 'react';"
)

with open('src/ProductWarehouse.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('ProductWarehouse.jsx useRef 导入修复完成')
