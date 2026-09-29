#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""loocinsight：注入 CSS 隱藏靜態站上失效的搜尋框（idempotent，marker 守護）。
   Elementor 巢狀 markup 硬删易爆版，故用 display:none。用法：python3 hide-search.py [site目錄]"""
import os, sys, glob
SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
MARK = "loocinsight-hide-search"
CSS = ('<style id="%s">/* remove non-functional search (static site) */'
       '.vamtam-search-form,.elementor-widget-search-form,.vamtam-theme-search,'
       'form.elementor-search-form,form[role="search"]{display:none!important}'
       '</style>') % MARK
n = 0
for f in glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True):
    s = open(f, encoding="utf-8", errors="ignore").read()
    if MARK in s or "</head>" not in s: continue
    open(f, "w", encoding="utf-8").write(s.replace("</head>", CSS + "\n</head>", 1)); n += 1
print(f"  搜尋隱藏 CSS：注入 {n} 頁（已有 marker 則跳過）")
print("✓ hide-search 完成")
