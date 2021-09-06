#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
from PIL import Image
import numpy as np


class yabiinfo:
    """讀取 yabi 圖片資訊"""

    data: bytes
    colormode: int
    width: int
    height: int
    size: int
    color: list[int] = []
    aisle: list[bool] = []

    def val255d(self, vals: list[int]):
        """
        將多位十六進位制轉換回十進位制數字
        vals: list[int]  十六進位制陣列
        """
        # 例如結果 [189, 219, 108] 往回算到 12345678 :
        # (189*255+219)*255+108
        # 4位时，最大值 ((255*255+255)*255+255)*255+255=4244897280
        vallen: int = len(vals)
        num: int = vals[0]
        for i in range(vallen):
            if i < vallen - 1:
                num = num * 255 + vals[i + 1]
        return num

    def loaddata(self, file: str):
        """
        從檔案將所有資料讀入
        file: str  檔案路徑
        """
        with open(file, 'rb') as f:
            self.data = f.read()
            f.close()

    def info(self, output=True) -> list:
        """
        獲取圖片資訊
        output: bool  輸出資訊，否則只輸出錯誤
        """
        if self.data[0] != 89 or self.data[1] != 66:
            if output:
                print("错误: 不是 YABI 格式")
            quit()
        p = 2  # 下標
        version = self.data[p]
        if version != 1:
            if output:
                print("错误: 不支持的文件版本 " + str(version))
            quit()
        if output:
            print("图像格式: 雅诗位图图像" + str(version))
        p += 1
        self.colormode = self.data[p]
        if self.colormode == 1:
            if output:
                print("颜色模式: 单色模式")
        else:
            if output:
                print("错误: 不支持的颜色模式")
            quit()
        p += 1
        if self.colormode < 3: # 單色和灰度模式可以指定基礎顏色和通道
            for _ in range(4):
                self.color.append(self.data[p])
                p += 1
            print("基础颜色: " + ','.join([str(x) for x in self.color]))
            aislebin = bin(self.data[p])
            aislebini = 0
            for v in aislebin:
                if aislebini > 1:
                    if v == "1":
                        self.aisle.append(True)
                    else:
                        self.aisle.append(False)
                aislebini += 1
            print("影响RGBA通道: " + ','.join([str(x) for x in self.aisle]))
            p += 1
        sizelen: int = int(self.data[p])
        p += 1
        sizearr: list[int] = []
        for _ in range(sizelen):
            sizearr.append(self.data[p])
            p += 1
        self.width: int = self.val255d(sizearr)
        if output:
            print("宽度: " + str(self.width))
        p += 1
        sizearr: list[int] = []
        for _ in range(sizelen):
            sizearr.append(self.data[p])
            p += 1
        self.height: int = self.val255d(sizearr)
        if output:
            print("高度: " + str(self.height))
        self.size: int = self.width * self.height
        if output:
            print("像素数: " + str(self.size))
        self.data = self.data[p:]

    def toarray(self) -> list:
        """重新构建回 Image"""
        read = 0
        all: list[int] = []
        line: list[int] = []
        row: list[int] = []
        for d in self.data:
            binunit = str(bin(d))[2:].zfill(8)
            for char in binunit:
                charnum: int = 255
                if char == "0":
                    charnum = 0
                px: list[int] = self.color
                for i in range(4):
                    if self.aisle[i] == True:
                        px[i] = charnum
                row.append(px)
                if len(row) == self.width:
                    line.append(row)
                    row = []
                if len(line) == self.height:
                    all.append(line)
                    line = []
                read += 1
                if read == self.size:
                    return all[0]
        print("错误: 意外的文件末端")
        return all

    def argvin(self):
        """獲取命令列輸入並開始進行處理"""
        filein: str = ""
        if len(sys.argv) >= 2:
            filein = sys.argv[1]
            self.loaddata(filein)
            self.info()
            imglist = self.toarray()
            imgarr: np.ndarray = np.dstack(imglist)
            imgarr = imgarr.astype("uint")
            img: Image = Image.fromarray(imgarr, "RGBA")
            # img.show()
            if len(sys.argv) >= 3:
                img.save(sys.argv[2])
            else:
                img.save(filein + ".png")
        else:
            print("use:")
            print("python3 yabiinfo.py <yabi file> <new image file>")
            quit()


conv = yabiinfo()
conv.argvin()
