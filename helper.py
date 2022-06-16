# 此為繪圖程式，負責繪出訓練數據的二維陣列圖。
# This is a plotting program, which is responsible for plotting a two-dimensional array of training data.

'''Python 的視覺化套件有靜態的 matplotlib 跟 seaborn 套件，與動態的 bokeh 套件。
matplotlib可以繪製許多類型的二維陣列圖表，例如直方圖 (Histogram)、散佈圖 (Scatter plot)、
折線圖 (Line plot)、長條圖 (Bar plot)、盒鬚圖 (Box plot)等。'''
import matplotlib.pyplot as plt
'''Display a Python object in all frontends. By default all representations will be computed and sent to the frontends. 
Frontends can decide which representation is used and how. In terminal IPython this will be similar to using print() , 
for use in richer frontends see Jupyter notebook examples with rich display logic.'''
from IPython import display

plt.ion()   # 二維陣列圖

'''定義繪製折線圖的方式。以這個程式為例，我們這次使用matplotlib的目的是繪製折線圖，
所以要使用matplotlib的plot()方法，如下所示。'''
def plot(scores, mean_scores, snake):
    # 開啟多個視窗，分別對綠蛇(snake == 'GREEN')及黃蛇(else)繪製圖表
    if snake == 'GREEN':
        plt.figure(1)
    else:
        plt.figure(2)
    display.clear_output(wait=True) # cls
    display.display(plt.gcf())      # print / get current figure
    plt.clf()                       # clear current figure
    
    # 設定圖表標題為 Training + 蛇的名稱
    plt.title('Training ' + snake)
    # 定義x軸的名稱為 Number of Games
    plt.xlabel('Number of Games')
    # 定義y軸的名稱為 Score
    plt.ylabel('Score')
    # 開始繪製分數(scores)與平均分數(mean_scores)的折線圖
    plt.plot(scores)
    plt.plot(mean_scores)
    # 限制y軸的最小值為0，並開始繪製刻度數值並調整好刻度間距
    plt.ylim(ymin=0)
    plt.text(len(scores) - 1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores) - 1, mean_scores[-1], str(mean_scores[-1]))
