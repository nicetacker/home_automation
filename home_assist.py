#coding: utf-8

import broadlink
import os
import sys
import json
import pycurl

class Command:
  def __init__(self, target, action):
    self.target_ = target.lower()
    self.action_ = action.lower()

  def target(self):
    return self.target_
 
  def action(self):
    return self.action_

  def command(self):
    return "[%s] %s" % (self.target_, self.action_)

  def Dispatch(self):
    raise NotImplementedError()


class NullCommand(Command):
  def Dispatch(self):
    return False


class IRCommand(Command):
  u""" eRemote mini用コマンド"""
  def __init__(self, target, action, dev_file, ir_file):
    super().__init__(target, action)
    self.ir_cmd_ = bytearray.fromhex(open(ir_file, "r").readline().strip())
    self.dev_file_ = dev_file

  def parse_devfile_(self, f):
    vals = open(f, "r").readline().split()
    dev_type = int(vals[0], 0)
    host = vals[1]
    mac = bytearray.fromhex(vals[2])
    return (dev_type, host, mac)

  def Dispatch(self):
    dev_type, host, mac = self.parse_devfile_(self.dev_file_)
    dev = broadlink.gendevice(dev_type, (host, 80), mac)
    dev.auth()
    dev.send_data(self.ir_cmd_)
    return True


class WebHookCommand(Command):
  u""" IFTTT webhook用コマンド"""
  def __init__(self, target, action, key, event):
    super().__init__(target, action)
    self.event_ = event
    self.key_ = key 

  def Dispatch(self):
    url = "https://maker.ifttt.com/trigger/%s/with/key/%s" % (self.event_, self.key_)
    options = {"value1": ""}

    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, json.dumps(options))
    c.perform()

    return True


class CommandFacory:
  def __init__(self):
    self.cmd = {}
    self.load_command()

  def load_command(self):
    f = open("config.json", "r") 
    json_dict = json.load(f)

    # eRemote mini 用のコマンドファイルを読み込む
    dev_file  = json_dict["ir_cmd"]["device"]
    cmd_files = json_dict["ir_cmd"]["cmd_files"]
    remo_files = os.listdir(cmd_files)
    for f in remo_files:
      target, action = [w.lower() for w in f.split(".")]
      if target not in self.cmd:
          self.cmd[target] = {}
      self.cmd[target][action] = IRCommand(target, action, dev_file, os.path.join(cmd_files, f))

    # WebHook用のコマンド
    key = json_dict["webhook"]["key"]
    for e in json_dict["webhook"]["events"]:
      target = e["target"].lower()
      action = e["action"].lower()
      event =  e["event"]
      if target not in self.cmd:
          self.cmd[target] = {}
      self.cmd[target][action] = WebHookCommand(target, action, key, event)

  def Create(self, request):
    if "." not in request:
        return NullCommand("unknown", "unknown")
    target, action = [req.strip().lower() for req in request.split(".")]  
    cmd = self.cmd[target][action]
    if not cmd:
      return NullCommand(target, action)
    return cmd

  def AvailableCommands(self):
    return self.cmd 


class HomeAssistant:
  def __init__(self):
    self.Factory = CommandFacory()

  def Show(self):
    cmds = self.Factory.AvailableCommands()
    msg = "利用可能なコマンドはこちらです！:\n"
    for action in cmds:
      msg += "  [%-10ls]: %s\n" % (action, ", ".join(sorted(cmds[action]))) 
    return msg 

  def Send(self, command):
    cmds = self.parse_command(command)
    successed = []
    failed = []

    # コマンドを送るよ
    for cmd in cmds:
      req_str = cmd.command()
      ret = cmd.Dispatch()
      if(ret):
        successed.append(req_str)
      else:
        failed.append(req_str)

    msg = ""
    if(successed):
      msg += "コマンドを送ったよ！\n"
      msg += "  %s\n" % (", ".join(successed))
    if(failed):
      msg += "コマンドを送れませんでした。。。\n"
      msg += "  %s\n" % (", ".join(failed))

    return msg

 
  def parse_command(self, command_str):
    ret = []
    requests = [c.strip().lower() for c in command_str.split(",")]
    for req in  requests:
      cmd = self.Factory.Create(req)
      ret.append(cmd)

    return ret


if __name__ == "__main__":
  assistant = HomeAssistant()
  ret = assistant.Send(",".join(sys.argv[1:]))
  print (ret)
  print (assistant.Show())

