# 此為繪圖程式，負責繪出訓練數據的二維陣列圖。

import matplotlib.pyplot as plt
from IPython import display

plt.ion()   # 二維陣列圖

def plot(scores, mean_scores, snake):
    if snake == 'GREEN':    # 開啟多個視窗
        plt.figure(1)
    else:
        plt.figure(2)
    display.clear_output(wait=True) # cls
    display.display(plt.gcf())      # print / get current figure
    plt.clf()                       # clear current figure
    
    plt.title('Training ' + snake)
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores) - 1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores) - 1, mean_scores[-1], str(mean_scores[-1]))
