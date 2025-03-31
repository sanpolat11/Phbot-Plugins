from phBot import *
from threading import Timer
import QtBind
import struct
import json
import urllib.request
import os
import time

name = 'Skillrator'
version = 1.0
NewestVersion = 0
path = get_config_dir() + name + "\\"

gui = QtBind.init(__name__, name)

# GUI Elements
lblCurrentSkills = QtBind.createLabel(gui, 'Mevcut Beceriler', 70, 10)
lstCurrentSkills = QtBind.createList(gui, 10, 30, 200, 200)
buttonGetSkills = QtBind.createButton(gui, 'button_get_skills', ' Becerileri Yenile ', 60, 240)

lblTargetSkills = QtBind.createLabel(gui, 'Hedef Beceriler', 350, 10)
lstTargetSkills = QtBind.createList(gui, 300, 30, 200, 200)
lblSave = QtBind.createLabel(gui, 'Otomatik Kaydedilir', 350, 240)

buttonAdd = QtBind.createButton(gui, 'button_add', ' Ekle ', 215, 100)
buttonRemove = QtBind.createButton(gui, 'button_remove', ' Sil ', 215, 125)
cbxEnable = QtBind.createCheckBox(gui, 'cbxEnable_clicked', ' Etkin ', 225, 70)

def cbxEnable_clicked(checked):
    SaveConfig()

def button_get_skills():
    QtBind.clear(gui, lstCurrentSkills)
    skills = get_skills()
    for ID, skill in skills.items():
        QtBind.append(gui, lstCurrentSkills, skill['name'])

def button_add():
    selectedSkill = QtBind.text(gui, lstCurrentSkills)
    if not lstTargetSkill_exist(selectedSkill):
        QtBind.append(gui, lstTargetSkills, selectedSkill)
        SaveConfig()

def button_remove():
    selectedSkill = QtBind.text(gui, lstTargetSkills)
    QtBind.remove(gui, lstTargetSkills, selectedSkill)
    SaveConfig()

def lstTargetSkill_exist(skill):
    TargetSkills = QtBind.getItems(gui, lstTargetSkills)
    for TargetSkill in TargetSkills:
        if TargetSkill.lower() == skill.lower():
            return True
    return False

def GetSkillID(name):
    skills = get_skills()
    for ID, skill in skills.items():
        if skill['name'] == name:
            return ID

def GetSkillLevel(name):
    skills = get_skills()
    for ID, skill in skills.items():
        if skill['name'] == name:
            level = skill['servername'][-2:]
            return level

def UseSkill(skill_name):
    skill_id = GetSkillID(skill_name)
    if skill_id:
        # Doğru paket yapısı
        p = b'\x01\x04'  # Skill packet header
        p += struct.pack('<I', skill_id)
        p += b'\x01'  # Skill type
        p += struct.pack('<I', 0)  # Target ID (0 for self-cast)
        inject_joymax(0x7074, p, False)
        log('Eklenti: Beceri Kullanıldı [%s]' % skill_name)
        return True
    return False

def Skillrator(args):
    if QtBind.isChecked(gui, cbxEnable):
        TargetSkills = QtBind.getItems(gui, lstTargetSkills)
        if TargetSkills:
            skill = TargetSkills[0]  # İlk beceriyi kullan
            if UseSkill(skill):
                return 1000  # 1 saniye bekle
    return 0

def joined_game():
    Timer(4.0, LoadConfigs, ()).start()

def GetConfig():
    return path + get_character_data()['server'] + "_" + get_character_data()['name'] + ".json"

def SaveConfig():
    data = {}
    data['Enable'] = QtBind.isChecked(gui, cbxEnable)
    data["TargetSkills"] = QtBind.getItems(gui, lstTargetSkills)
    with open(GetConfig(), "w") as f:
        f.write(json.dumps(data, indent=4))

def LoadConfigs():
    if os.path.exists(GetConfig()):
        data = {}
        with open(GetConfig(), "r") as f:
            data = json.load(f)
        if "Enable" in data:
            QtBind.setChecked(gui, cbxEnable, data["Enable"])
        if "TargetSkills" in data:
            QtBind.clear(gui, lstTargetSkills)
            for skill in data['TargetSkills']:
                QtBind.append(gui, lstTargetSkills, skill)

def CheckForUpdate():
    global NewestVersion
    if NewestVersion == 0:
        try:
            req = urllib.request.Request('https://raw.githubusercontent.com/YourUsername/phBot-Plugins/master/Skillrator.py', headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as f:
                lines = str(f.read().decode("utf-8")).split()
                for num, line in enumerate(lines):
                    if line == 'version':
                        NewestVersion = int(lines[num+2].replace(".",""))
                        CurrentVersion = int(str(version).replace(".",""))
                        if NewestVersion > CurrentVersion:
                            log('Eklenti: Yeni bir güncelleme var = [%s]!' % name)
                            lblUpdate = QtBind.createLabel(gui, 'Yeni Bir Güncelleme Mevcut. Yüklemek için Tıkla ->', 100, 283)
                            button1 = QtBind.createButton(gui, 'button_update', ' Güncelle ', 350, 280)
        except:
            pass

def button_update():
    path = get_config_dir()[:-7]
    if os.path.exists(path + "Plugins/" + "Skillrator.py"):
        try:
            os.rename(path + "Plugins/" + "Skillrator.py", path + "Plugins/" + "SkillratorBACKUP.py")
            req = urllib.request.Request('https://raw.githubusercontent.com/YourUsername/phBot-Plugins/master/Skillrator.py', headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as f:
                lines = str(f.read().decode("utf-8"))
                with open(path + "Plugins/" + "Skillrator.py", "w+") as f:
                    f.write(lines)
                    os.remove(path + "Plugins/" + "SkillratorBACKUP.py")
                    log('Eklenti Başarıyla Güncellendi, Kullanmak için Eklentiyi Yeniden Yükleyin.')
        except Exception as ex:
            log('Güncelleme Hatası [%s] Lütfen Manuel Olarak Güncelleyin veya daha Sonra Tekrar Deneyin.' % ex)

CheckForUpdate()

Timer(1.0, LoadConfigs, ()).start()
log('Eklenti: %s v%s Yüklendi.' % (name, version))

if not os.path.exists(path):
    os.makedirs(path)
    log('Eklenti: %s Klasörü Oluşturuldu.' % name) 