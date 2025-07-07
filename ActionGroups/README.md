# 'ActionGroups'文件夹
存放动作组文件

## 'load_action_groups.py'用于提前加载动作组到内存,在'Controll.py'使用'from ActionGroups.load_action_groups import action_groups' 进行调用
- 通过 `group_list` 设置需要提前载入的动作组，减少运行时磁盘读取。
- 载入后的内容保存在 `action_groups` 字典中，供手动模式直接调用。

### 'load_action_groups.py'中的'group_list'列表，表示你所要预加载的几个动作组
- 在该列表中写入动作组名称，即可在启动时自动从当前目录加载对应的 `.json` 文件。
- 未列出的动作组在首次使用时再动态读取。

