#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
from PIL import Image
import numpy as np

class png2yabi:

    def val255x(self, val: int) -> list[int]:
        """
        使用多位十六進位制儲存較大十進位制數字
        val: int  十進位制數字
        """
        # 得出的結果 [189, 219, 108] 往回算到 12345678 :
        # (189*255+219)*255+108
        # 4位最大值 ((255*25 5+255)*255+255)*255+255=4244897280
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
        return data


    def convert(self, file: str, tofile: str, mode: int):
        """
        將常用圖片格式轉換為雅詩點陣圖格式
        file  : str    原始檔路徑
        tofile: str  轉換後路徑(*.yabi)
        mode  : int    色彩模式 1.單色 2.灰度 3.RGB 4.RGBA
        """
        img: Image = Image.open(file)
        imagearray: np.ndarray = np.array(img)
        data: list[int] = [
            89,  # Y標識
            66,  # B標識
            1,  # 版本
            mode
        ]
        # 寬度頭
        widtharr: list[int] = self.val255x(len(imagearray[0]))
        data.append(len(widtharr))  # 接下來多少位表示寬度
        data.extend(widtharr)  # 寫入寬度位
        # 高度头
        heightarr: list[int] = self.val255x(len(imagearray))
        data.append(len(heightarr))  # 接下來多少位表示高度
        data.extend(heightarr)  # 寫入高度位
        # 長度頭
        totali: int = 0
        for line in imagearray:
            for row in line:
                totali += 1
        totalarr: list[int] = self.val255x(totali)
        data.append(len(totalarr))  # 接下來多少位表示長度
        data.extend(totalarr)  # 寫入長度位
        # 開啟寫入流
        with open(tofile, "wb") as f:
            f.write(bytes(data)) # 寫入標頭檔案，下面寫入資料
            tmphex: str = ""
            for line in imagearray:
                rowtmp: list[str] = []
                for row in line:
                    r: int = row[0]
                    g: int = row[1]
                    b: int = row[2]
                    if mode == 1: # 單色模式（每8個畫素記錄一個16進位制）
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
        fin: str = ""
        fout: str = ""
        mode: str = ""
        if len(sys.argv) >= 3:
            mode = sys.argv[1]
            fin = sys.argv[2]
        else:
            print("use:")
            print("python3 img2yabmp.py <color mode> <image file> <new yabmp file>")
            quit()
        if len(sys.argv) >= 4:
            fout = sys.argv[3]
        else:
            fout = fin + ".yabi"
        self.convert(fin, fout, int(mode))

conv = png2yabi()
conv.argvin()