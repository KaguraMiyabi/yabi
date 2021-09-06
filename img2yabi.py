#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
from PIL import Image
import numpy as np


class png2yabi:
    """將圖片轉換為yabi"""

    def val255x(self, val: int) -> list[int]:
        """
        使用多位十六進位制儲存較大十進位制數字
        val: int  十進位制數字
        """
        data: list[int] = [val]

        def sizeval():
            x: int = 0
            while data[0] > 255:
                x += 1
                data[0] -= 255
            data.insert(0, x)
            if x > 255:
                sizeval()
        sizeval()
        if data[0] == 0:
            data.pop(0)
        return data

    def convert(self, file: str, tofile: str, mode: int, color=""):
        """
        將常用圖片格式轉換為雅詩點陣圖格式
        file  : str  原始檔路徑
        tofile: str  轉換後路徑(*.yabi)
        mode  : int  色彩模式 1.單色 2.灰度 3.RGB 4.RGBA
        """
        img: Image = Image.open(file)
        img = img.convert("RGBA")
        imagearray: np.ndarray = np.array(img)
        # 基本資訊
        data: list[int] = [
            89,  # Y標識
            66,  # B標識
            1,  # 版本
            mode,  # 色彩模式
        ]
        if mode < 3:
            # 單色和灰度模式可以指定基礎顏色和通道
            if len(color) == 0:
                color = "0,0,0,255,1110"
            basecolorArr: list[str] = color.split(',')
            # 受影響的通道（RGBA四個通道由二進位制組成十六進位制）
            for i in range(len(basecolorArr)):
                if i < 4:  # RGBA
                    data.append(int(basecolorArr[i]))
                elif i == 4:
                    data.append(int(basecolorArr[i], 2))
        # 寬度
        widtharr: list[int] = self.val255x(len(imagearray[0]))
        data.append(len(widtharr))  # 接下來多少位表示寬度
        data.extend(widtharr)  # 寫入寬度位
        # 高度
        heightarr: list[int] = self.val255x(len(imagearray))
        data.append(len(heightarr))  # 接下來多少位表示高度
        data.extend(heightarr)  # 寫入高度位
        # 開啟寫入流
        with open(tofile, "wb") as f:
            f.write(bytes(data))  # 寫入標頭檔案，下面寫入資料
            tmphex: str = ""
            for line in imagearray:
                rowtmp: list[str] = []
                for row in line:
                    r: int = row[0]
                    g: int = row[1]
                    b: int = row[2]
                    if mode == 1:  # 單色模式（每8個畫素記錄一個16進位制）
                        if r > 128 or g > 128 or b > 128:
                            tmphex += "1"
                        else:
                            tmphex += "0"
                        if len(tmphex) == 8:
                            base2: int = int(tmphex, 2)
                            rowtmp.append(base2)
                            tmphex = ""
                f.write(bytes(rowtmp))
            # 單色模式解決殘餘快取
            if mode == 1:
                tmphexlen: int = len(tmphex)
                if tmphexlen > 0:
                    diff: int = 8 - tmphexlen
                    tmphex += ("0" * diff)
                    f.write(bytes([tmphex]))
            # 新檔案寫入結束
            f.close()

    def argvin(self):
        """獲取命令列輸入並開始進行處理"""
        filein: str = ""
        fileout: str = ""
        mode: str = ""
        if len(sys.argv) >= 3:
            mode = sys.argv[1]
            filein = sys.argv[2]
        else:
            print("use:")
            print("python3 img2yabi.py <color mode> <image file> <new yabi file>")
            quit()
        if len(sys.argv) >= 4:
            fileout = sys.argv[3]
        else:
            fileout = filein + ".yabi"
        self.convert(filein, fileout, int(mode))


conv = png2yabi()
conv.argvin()
