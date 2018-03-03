#coding: utf-8

import broadlink
import subprocess 
import os
import sys
import json


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
    raise ""


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
    dev_type, host, mac = self.parse_devfile_(self.dev_file)
    dev = broadlink.gendevice(dev_type, (host, 80), mac)
    dev.auth()
    dev.send_data(self.ir_cmd_)
    return True


class WebHookCommand(Command):
  u""" IFTTT webhook用コマンド"""
  def __init__(self, target, key, action, event):
    super().__init__(target, action)
    self.event_ = event
    self.key_ = key 

  def Dispatch(self):
    url = "https://maker.ifttt.com/trigger/%s/with/key/%s" % (self.event_, self.key_)
    cmd = ["curl", "-X" , "POST", "-H", "Content-Type: application/json", "-d", "{\"value1\": \"aaa\"}", url] 
    subprocess.call(cmd)
    return True


class CommandFacory:
  def __init__(self):
    self.cmd = []
    self.load_command()

  def load_command(self):
    f = open("config.json", "r") 
    json_dict = json.load(f)

    # eRemote mini 用のコマンドファイルを読み込む
    dev_file  = json_dict["ir_cmd"]["device"]
    cmd_files = json_dict["ir_cmd"]["cmd_files"]
    remo_files = os.listdir(cmd_files)
    for f in remo_files:
      device, action = f.split(".")
      cmd = IRCommand(device, action, dev_file, os.path.join(cmd_files, f))
      self.cmd.append(cmd)
 
    # WebHook用のコマンド
    key = json_dict["webhook"]["key"]
    for event in json_dict["webhook"]["events"]:
      self.cmd.append(WebHookCommand(event["target"], key, event["action"], event["event"]))

  def Create(self, request):
    if "." not in request:
        return NullCommand("unknown", "unknown")
    target, action = [req.strip().lower() for req in request.split(".")]  
    cmd = [c for c in self.cmd if c.target() == target and c.action() == action]
    if not cmd:
      return NullCommand(target, action)
    
    if len(cmd) != 1:
      print("WARN: Can't detect single command:", request)
    return cmd[0]


class HomeAssistant:
  def __init__(self):
    self.Factory = CommandFacory()

  def Show(self):
    #msg = "利用可能なコマンドはこちらです！:\n"
    #for device in tmp:
    #  msg += "    [%10s]: %s\n" % (device, ", ".join(sorted(tmp[device])))
    return 

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

