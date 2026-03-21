# Credential-Issuer

> 數位憑證發行系統 · 串接台灣數發部 OID4VCI 沙盒 API

<p>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="45"/> Python &nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg" height="45"/> Flask &nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" height="45"/> HTML5 &nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vercel/vercel-original.svg" height="45"/> Vercel &nbsp;&nbsp;
</p>

## Overview

本系統為 H-CAP 普惠金融平台的子系統，負責向使用者發行可驗證的數位憑證。透過串接台灣數位部（數發部）數位身分錢包沙盒 API，實作 OID4VCI 憑證發行流程，支援 QR Code 掃描與 DeepLink 兩種方式將憑證傳入使用者數位憑證皮夾。

## Core features

| Feature | Description |
|---|---|
| OID4VCI 發行流程 | 符合數發部沙盒規範的完整憑證發行流程 |
| QR Code + DeepLink | 雙管道將憑證傳入使用者數位身分錢包 |
| Vercel Serverless Proxy | 繞過數發部沙盒 API 的 CORS 限制 |

## Tech stack

- **Backend：** Python Flask
- **Frontend：** HTML / JavaScript
- **Proxy：** Vercel Serverless Function（CORS bypass）
- **Identity Protocol：** OID4VCI / OID4VP — 數發部數位憑證沙盒 API

## Background

數發部數位身分錢包沙盒 API 不允許直接從前端跨域呼叫，透過部署 Vercel Serverless Proxy 作為中介層，解決 CORS 限制，確保 QR Code 生成與 DeepLink 回傳流程正確運作。本系統作為 [H-CAP](https://github.com/Evan-Jiamg/H-CAP) 的憑證發行模組，獨立維護。
