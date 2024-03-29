# 此為Deep Q Learning的部分，定義了Linear_QNet與QTrainer兩個函式。
'''關於這些Q值、學習率(lr，Learning Rate)、損失函數、貝爾曼方程(Bellman equation)等術語，
詳細說明請看書面報告。如果仍有不清楚的詞彙的話，請對照agent.py的變數與註解。'''

# PyTorch為製作機器學習常用的模組。
# 除了os之外，以下這些都是用PyTorch引入的模組。
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
'''os模組是關於作業系統操作呼叫的相關模組。它提供了一些系統級別的操作，例如對檔案進行重新命名、刪除等一系列操作，
將程式碼改用os的模式撰寫可以支援跨平臺。'''
import os

class Linear_QNet(nn.Module):
    
    # 初始化設定值
    def __init__(self, input_size, hidden_size, output_size):
        super(Linear_QNet, self).__init__()  # 繼承 parent 的屬性 == nn.Module.__init__()
        """ parent 的屬性
        (OrderedDict: 有序字典)
        self._parameters = OrderedDict()    -> 儲存管理 nn.Parameter 型別的引數
        self._buffers = OrderedDict()
        self._backward_hooks = OrderedDict()
        self._forward_hooks = OrderedDict()
        self._forward_pre_hooks = OrderedDict()
        self._state_dict_hooks = OrderedDict()
        self._load_state_dict_pre_hooks = OrderedDict()
        self._modules = OrderedDict()       -> 儲存管理 nn.Module 型別的引數
        """
        # 設定兩個子模組
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    # 定義將子模組拼接的函式
    def forward(self, x):   # 預測(prediction)
        x = F.relu(self.linear1(x)) # 對第一層 linear1 使用 reLU
        x = self.linear2(x)         # 第二層直接輸出
        return x

    # 定義存檔(保存訓練數據)的函式
    def save(self, file_name='model.pth'):
        model_folder_path = 'model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        """ os.path
        OS 模塊首先判斷當前環境是否安裝了 posixpath.py,
        如果安裝了 posixpath.py 則直接導入 posixpath,
        如果沒有則繼續判斷是否安裝了 ntpath.py,
        如果安裝了 ntpath.py 則引用 ntpath.py,
        否則拋出 ImportError。
        """
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)    # 儲存 OrederDict

class QTrainer:
    # 初始化設定值
    def __init__(self, model, lr, gamma):
        self.lr = lr # Learning Rate(學習率)
        self.gamma = gamma
        self.model = model
        # 優化器
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr) # 可學習參數
        # 損失函數(loss function)
        self.criterion = nn.MSELoss()

    # 定義管理訓練步驟的函式
    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)  # 多維矩陣
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, ) # tuple with only one value

        # 1: 以目前狀態預測Q值 (predicted Q values with current state)
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action).item()] = Q_new
        
        # 2: 當尚未Game Over時，使用貝爾曼方程的結論 Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        # pred.clone()
        # preds[argmax(action)] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()
