---
title: '專家系統操作注意事項'
disqus: hackmd
---

專家系統操作注意事項：
===
![downloads](https://img.shields.io/github/downloads/atom/atom/total.svg)
![build](https://img.shields.io/appveyor/ci/:user/:repo.svg)
![chat](https://img.shields.io/discord/:serverId.svg)


[TOC]

## 使用前準備事項
下載更新版的專家系統後，請更換以下檔案，以免過往資料遺失。
1. Diagnosis_Rules.xlsm [專家系統知識規則庫]
2. Dataset資料夾中的xxx.csv
* SiteEva_Table.csv [茶園登入資料]
* Soils_Test.csv [各茶區土壤速測資料]
* Planting_Water.csv [各茶區水用量資料]
* Planting_Fertilizer_(internal_code) [各茶區肥料用量資料]
3. Code_Recode.json [茶園流水編號記錄檔]
***重要：請確保流水標號與 "SiteEvaTable.csv" 的最後一筆資料相符合***
```
{"551": "0012", "555": "000A"}

以上表示 "551" 茶區標號到 "0012", "555" 茶區標號到 "000A"
一般正常透過介面輸入，不需要動，如果有手動更新 "SiteEva_Table.csv"，則必須手動更新記錄檔，否則會導致系統錯誤。
```
4. 申雍老師的程式執行檔(如果有更新可以覆蓋)
* UAV_Analysis.exe
* ReportMaker.exe
* NodeAnswer.exe
* CropVISTMapInfoTWN.exe
* CropVISTMapInfoENG.exe
* CropPlantationLocation.exe
* 
5. 新增Save資料夾(儲放診斷結果，如果有則不用)
6. 在Photo中新增TempFile資料夾(儲放天氣、衛星影像等暫存圖檔，如果有則不用)
8. Start enjoyed it!

## 專家系統下載
請至Download下載最新日期主程式!
```
https://github.com/NCHU-rogen/ExpertSystem_Project/blob/master/Download/ExpertSystemForTea_20210107.rar
```
![](https://i.imgur.com/ncYoPsY.png)


## Appendix and FAQ

:::info
**Find this document incomplete?** Leave a comment!
:::

###### tags: `Expert System` `Documentation`
