import time, re, os, json
from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen

# from configs import SNMPConfig
from configs import BaseConfig

from configs import get_logger
task_logger = get_logger('task_log')

# oid值
oid_dict = {
    # arp表oid
    "arp_table": (1, 3, 6, 1, 2, 1, 4, 22, 1, 2),
    # mac地址表oid
    "mac_address_table": (1, 3, 6, 1, 2, 1, 17, 7, 1, 2, 2, 1, 2),
    # "mac_address_table": (1, 3, 6, 1, 2, 1, 17, 4, 3, 1, 2),
    # 接口VLAN类型oid  1.3.6.1.4.1.25506.8.35.1.1.1.5
    "port_type": (1, 3, 6, 1, 4, 1, 25506, 8, 35, 1, 1, 1, 5),
    # 接口索引对应接口名称 1.3.6.1.2.1.2.2.1.2
    "port_index": (1, 3, 6, 1, 2, 1, 2, 2, 1, 2),
    # 系统名称oid，获取交换机system name 1, 3, 6, 1, 2, 1, 1, 5
    "system_name": (1, 3, 6, 1, 2, 1, 1, 5),
    # IP地址+子网掩码oid （ipAdEntNetMask）.1.3.6.1.2.1.4.20.1.3
    "ip_mask": (1, 3, 6, 1, 2, 1, 4, 20, 1, 3),
    # IP地址（ipAdEntAddr）1.3.6.1.2.1.4.20.1.1
    # "test": (1, 3, 6, 1, 2, 1, 4, 20, 1, 1),
}


# 点分十进制转十六进制mac地址格式
def convert_to_hex_format(ip_string):
    # 将输入字符串按点分割
    parts = ip_string.split('.')
    # 初始化一个空列表来存储十六进制值
    hex_values = []
    # 遍历
    for part in parts:
        # 将数字转换为十六进制字符串，并去掉前导 '0x'
        hex_part = format(int(part), 'x')
        # 如果长度为1，则在前面补0
        if len(hex_part) == 1:
            hex_part = '0' + hex_part
        # 添加到列表中
        hex_values.append(hex_part)
    # 每两个十六进制值组合成一个字符串，并用 '-' 分隔
    result = '-'.join(''.join(hex_values[i:i + 2]) for i in range(0, len(hex_values), 2))
    return result


class Snmp:
    def __init__(self, ip, community, mp_model=1, port=161, timeout=1000):
        self.ip = ip
        self.community = community
        self.mpModel = mp_model
        self.port = port
        self.timeout = timeout
        self.result = {}

    def snmp_walk(self, oid):
        iterator = bulkCmd(SnmpEngine(),
                           CommunityData(self.community),
                           UdpTransportTarget((self.ip, self.port)),
                           ContextData(),
                           0, 50,
                           ObjectType(ObjectIdentity(oid)),
                           lexicographicMode=False)
        result = []
        for (errorIndication, errorStatus, errorIndex, varBinds) in iterator:

            if not errorIndication and not errorStatus:
                for varBind in varBinds:
                    oid_value = [x.prettyPrint() for x in varBind]
                    if oid_value and len(oid_value) >= 2 and str(oid_value[1]).strip() != '':
                        result.append(oid_value)
            else:
                # break
                # continue
                return

        return result

    def set_result(self, name, oid_result):
        if oid_result and len(oid_result) >= 1 and len(oid_result[0]):
            self.result.update({name: str(oid_result[0][1]).upper()})

    def get_arp_table(self, oid):
        arp_table = self.snmp_walk(oid)
        return arp_table

    def get_ip_mask(self, oid):
        ip_mask = self.snmp_walk(oid)
        return ip_mask

    def get_mac_address_table(self, oid):
        mac_table_address = self.snmp_walk(oid)
        return mac_table_address

    def get_port_index(self, oid):
        port_index = self.snmp_walk(oid)
        return port_index

    def get_port_type(self, oid):
        port_type = self.snmp_walk(oid)
        return port_type

    def get_system_name(self, oid):
        system_name = self.snmp_walk(oid)
        return system_name


# 对snmp轮询结果进行预处理-构造列表套字典
class PreSNMP:

    def __init__(self, **kwargs):
        self.system_name = None
        self.port_type = None
        self.port_name = None
        self.port_index = None
        self.mac_add = None
        self.vlan = None
        self.ip_address = None
        self.mac_address = None
        self.data = kwargs

    # 处理snmp轮询arp表返回的结果
    def p_arp_table(self):
        try:
            response_data = []
            for item in self.data['arp_table']:
                # 使用正则表达式匹配IP地址的部分
                ip = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$', item[0])
                if ip:
                    self.ip_address = ip.group(1)
                # 去掉0x前缀并转换为大写字母
                hex_mac = item[1][2:]
                if hex_mac:
                    # 使用字符串操作添加分隔符-
                    self.mac_address = '-'.join([hex_mac[i:i + 4] for i in range(0, len(hex_mac), 4)])

                item_data = {'ip': self.ip_address, 'mac_add': self.mac_address}
                response_data.append(item_data)
            return response_data
        except Exception:
            return False

    # 处理snmp轮询ip+mask返回的结果
    def p_ip_mask(self):
        try:
            response_data = []
            for item in self.data['ip_mask']:
                # 使用正则表达式匹配IP地址的部分
                ip = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$', item[0])
                if ip:
                    self.ip_address = ip.group(1)
                # 结果第二部分为子网掩码
                mask = item[1]

                item_data = {'ip': self.ip_address, 'mask': mask}
                response_data.append(item_data)
            return response_data
        except Exception:
            return False

    # 处理snmp轮询mac地址表返回的结果
    def p_mac_address_table(self):
        try:
            response_data = []
            for item in self.data['mac_address_table']:
                # 使用 split() 方法按照 '.' 分割字符串
                s_item = item[0].split('.')
                self.vlan = s_item[8]
                # 选择第13个元素开始到最后一个元素
                mac_address = '.'.join(s_item[9:])  # 从第13个元素开始取到最后一个部分
                self.mac_add = convert_to_hex_format(mac_address)
                self.port_index = item[1]

                item_data = {'vlan': self.vlan, 'mac_add': self.mac_add, 'port_index': self.port_index}
                response_data.append(item_data)
            return response_data
        except Exception:
            return False

    # 处理snmp轮询接口索引返回的结果
    def p_port_index(self):
        try:
            response_data = []
            for item in self.data['port_index']:
                # 使用 split() 方法按照 '.' 分割字符串
                s_item = item[0].split('.')
                # 取出最后一个元素 索引值
                self.port_index = s_item[-1]
                # 取出列表第二个元素 端口名称
                self.port_name = item[1]

                item_data = {'port_index': self.port_index, 'port_name': self.port_name}
                response_data.append(item_data)
            return response_data
        except Exception:
            return False

    # 处理snmp轮询接口类型返回的结果
    def p_port_type(self):
        try:
            response_data = []
            for item in self.data['port_type']:
                # 使用 split() 方法按照 '.' 分割字符串
                s_item = item[0].split('.')
                # 取出最后一个元素 索引值
                self.port_index = s_item[-1]
                # 取出列表第二个元素 端口类型 vLANTrunk(1), access(2), hybrid(3), fabric(4)
                self.port_type = item[1]

                item_data = {'port_index': self.port_index, 'port_type': self.port_type}
                response_data.append(item_data)
            return response_data
        except Exception:
            return False

    # 处理snmp轮询system name返回的结果
    def p_system_name(self):
        try:
            response_data = []
            for item in self.data['system_name']:
                # 取出列表第二个元素 system name
                self.system_name = item[1]

                item_data = {'system_name': self.system_name}
                response_data.append(item_data)
            return response_data
        except Exception:
            return False


# 处理snmp结果第一阶段，构造arp数据可写入数据库的数据行格式
class ProcessStage1:
    def __init__(self, res_arp_table, res_ip_mask, snmp_host):
        self.arp_table = res_arp_table
        self.ip_mask = res_ip_mask
        self.snmp_host = snmp_host
        self.res_data = None

    # 单台交换机从 arp ip+mask 计算得出ip+mask+network的数据
    def p_single_sw(self):
        from pear_admin.extensions.comm import get_network_info, ip_in_network

        res_data = []
        res_dict = {}

        for i in self.arp_table:
            for x in self.ip_mask:
                # 计算ip_mask网络号，当arp表IP地址在这个网段，将mac地址添加金res_ditc
                calc_network = get_network_info(x['ip'], x['mask'])
                calc_ip = ip_in_network(i['ip'], calc_network)
                if calc_ip:
                    res_dict = {'ip': i['ip'], 'mac_add': i['mac_add'], 'mask': x['mask'], 'snmp_host': self.snmp_host}
                    res_data.append(res_dict)
        return res_data


# 处理snmp结果第二阶段，构造端口数据可写入数据库的数据行格式
class ProcessStage2:
    def __init__(self, res_mac_table, res_port_index, res_port_type, res_system_name, snmp_host):
        self.mac_table = res_mac_table
        self.port_index = res_port_index
        self.port_type = res_port_type
        self.system_name = res_system_name
        self.snmp_host = snmp_host
        self.res_data = None

    # 单台交换机从 mac地址表，接口索引，接口类型 计算得出接口类型为access的数据
    def p_single_sw(self):
        mac_port_index_list = []
        type_port_index_list = []
        # 获取mac_table port_type 的接口索引值
        for i in self.mac_table:
            mac_port_index_list.append(i['port_index'])

        for i in self.port_type:
            if i['port_type'] == '2':
                type_port_index_list.append(i['port_index'])

        # 求mac_port_index_list和type_port_index_list的交集，结果为接口类型是access的mac地址表项
        # 转换列表为集合
        set1 = set(mac_port_index_list)
        set3 = set(type_port_index_list)
        # 求集合的交集
        intersection_set = set1.intersection(set3)
        # 将交集转换为列表
        intersection_list = sorted(intersection_set)

        # 内容为>> 设备名称，snmp地址，vlan，mac地址，接口名称
        res_data = []
        res_dict = {}

        for i in intersection_list:
            for x in self.mac_table:
                if x['port_index'] == i:
                    for y in self.port_index:
                        if y['port_index'] == i:
                            res_dict = {'system_name': self.system_name[0]['system_name'], 'snmp_host': self.snmp_host,
                                        'vlan': x['vlan'], 'mac_add': x['mac_add'], 'port_name': y['port_name']}
                    res_data.append(res_dict)
        return res_data


# 网关arp数据写入数据库
def add_stage1_data(data):
    from pear_admin.extensions import db
    from pear_admin.orms import IPTableORM, IPGroupORM
    from pear_admin.extensions.comm import get_network_info
    from datetime import datetime

    try:
        for item_data in data:
            # 提取需要插入或更新的字段值
            ip = item_data.get('ip')
            mac_add = item_data.get('mac_add')
            mask = item_data.get('mask')
            network = get_network_info(ip, mask)

            # 查询数据库中是否已存在相同的记录
            existing_record_ip = IPTableORM.query.filter_by(ip=ip).first()
            existing_record_mac = IPTableORM.query.filter_by(mac_add=mac_add).first()

            if existing_record_ip:
                # 更新记录
                # existing_record_ip.ip = ip
                existing_record_ip.mask = mask
                existing_record_ip.mac_add = mac_add
                existing_record_ip.network = network
                existing_record_ip.available = True
                existing_record_ip.updated_at = datetime.utcnow()
            elif existing_record_mac:
                # 更新记录
                existing_record_mac.ip = ip
                # existing_record_mac.mask = mask
                existing_record_mac.mac_add = mac_add
                existing_record_mac.network = network
                existing_record_mac.available = True
                existing_record_mac.updated_at = datetime.utcnow()
            else:
                # 计算网段信息的值，不能获取IP地址的掩码默认24位
                network = get_network_info(ip, mask)
                # 查询network网段是否已存在于数据库中
                existing_network_record = IPTableORM.query.filter_by(network=network).first()
                # 根据查询结果决定逻辑分支
                if existing_network_record:
                    # 如果网络已存在，则获取其所属的分组ID
                    ip_group_id = existing_network_record.ip_group_id
                else:
                    # 如果网络不存在，则准备创建新的网络记录，默认ip_group_id为1
                    ip_group_id = 1
                # 创建新的IPTable记录
                new_data = IPTableORM(ip=ip, mask=mask, mac_add=mac_add, network=network, available=True,
                                   ip_group_id=ip_group_id)
                db.session.add(new_data)

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        # print('写入或更新数据出错了' + str(e))
        task_logger.error('写入或更新数据出错了' + str(e))
        return False


# 更新stage2的内容到数据库
def add_stage2_data(data):
    from datetime import datetime
    from pear_admin.extensions import db
    from pear_admin.orms import IPTableORM,IPGroupORM

    try:
        for item_data in data:
            # 提取需要插入或更新的字段值
            system_name = item_data.get('system_name')
            snmp_host = item_data.get('snmp_host')
            vlan = item_data.get('vlan')
            mac_add = item_data.get('mac_add')
            port_name = item_data.get('port_name')

            # 查询数据库中是否已存在相同的记录
            existing_record = IPTableORM.query.filter_by(mac_add=mac_add).first()

            if existing_record:
                # 更新记录
                # existing_record.mac_add = mac_add
                existing_record.system_name = system_name
                existing_record.snmp_host = snmp_host
                existing_record.vlan = vlan
                existing_record.port_name = port_name
                existing_record.available = True
                existing_record.updated_at = datetime.utcnow()
            else:
                ip_group_id = 1
                # 创建新的IPTable记录
                new_data = IPTableORM(system_name=system_name,
                                   snmp_host=snmp_host,
                                   vlan=vlan,
                                   mac_add=mac_add,
                                   port_name=port_name,
                                   available=True,
                                   ip_group_id=ip_group_id)
                db.session.add(new_data)

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        # print('写入或更新数据出错了' + str(e))
        task_logger.error('写入或更新数据出错了' + str(e))
        return False


# 被定时任务调用的函数
def poll_write():
    try:
        # snmp_data_gw = SNMPConfig.SNMP_DATA_GW
        # snmp_data_acc = SNMPConfig.SNMP_DATA_ACC
        root_path = BaseConfig.ROOT_PATH
        # pear_admin\extensions\tasks\tasks.json
        snmp_config_path = os.path.join(root_path,'pear_admin','extensions','tasks','tasks.json')
        # 读取tasks.json文件提取信息
        with open(snmp_config_path,'r',encoding="utf-8") as f:
            snmp_config = json.load(f)
        snmp_data_gw = snmp_config['SNMP_DATA_GW']
        snmp_data_acc = snmp_config['SNMP_DATA_ACC']

        # 第一阶段结果处理 轮询网关设备获取arp-mac
        for item in snmp_data_gw:
            snmp = Snmp(item['snmp_host'], item['snmp_community'])
            arp_table = snmp.get_arp_table(oid_dict.get('arp_table'))
            ip_mask = snmp.get_ip_mask(oid_dict.get('ip_mask'))

            # 处理数据，网关不在汇聚交换机或接入交换机，轮询到的arp表是网管vlanif 网段的内容
            if arp_table and ip_mask:
                pre_snmp = PreSNMP(arp_table=arp_table, ip_mask=ip_mask)
                res_arp_table = pre_snmp.p_arp_table()
                res_ip_mask = pre_snmp.p_ip_mask()

                stage1_obj = ProcessStage1(res_arp_table, res_ip_mask, item['snmp_host'])
                res_data = stage1_obj.p_single_sw()
                # 写入arp数据
                flag = add_stage1_data(res_data)
                if not flag:
                    # print(f"{item['snmp_host']} 阶段1 写入或更新a数据出错>>>")
                    task_logger.error(f"{item['snmp_host']} 阶段1 写入或更新数据出错>>>")
                    continue
                # print(f"{item['snmp_host']} 阶段1 轮询任务完成>>>")
                task_logger.info(f"{item['snmp_host']} 阶段1 轮询任务完成>>>")
            else:
                # print(f"{item['snmp_host']} 阶段1 轮询任务出错>>>")
                task_logger.error(f"{item['snmp_host']} 阶段1 轮询任务出错>>>")
                # return False
                continue

        # 第二阶段结果处理 接入交换机和汇聚交换机 mac-address
        for item in snmp_data_acc:
            snmp = Snmp(item['snmp_host'], item['snmp_community'])
            mac_address_table = snmp.get_mac_address_table(oid_dict.get('mac_address_table'))
            port_index = snmp.get_port_index(oid_dict.get('port_index'))
            port_type = snmp.get_port_type(oid_dict.get('port_type'))
            system_name = snmp.get_system_name(oid_dict.get('system_name'))

            pre_snmp = PreSNMP(mac_address_table=mac_address_table, port_index=port_index, port_type=port_type,
                               system_name=system_name)
            res_mac_table = pre_snmp.p_mac_address_table()
            res_port_index = pre_snmp.p_port_index()
            res_port_type = pre_snmp.p_port_type()
            res_system_name = pre_snmp.p_system_name()

            # 处理stage2数据
            if mac_address_table and port_index and port_type and system_name:
                stage2_obj = ProcessStage2(res_mac_table, res_port_index, res_port_type, res_system_name, item['snmp_host'])
                res_data = stage2_obj.p_single_sw()
                # 写入端口数据
                flag = add_stage2_data(res_data)
                if not flag:
                    # print(f"{item['snmp_host']} 阶段2 写入或更新a数据出错>>>")
                    task_logger.error(f"{item['snmp_host']} 阶段2 写入或更新a数据出错>>>")
                    continue
                # print(f"{item['snmp_host']} 阶段2 轮询任务完成>>>")
                task_logger.info(f"{item['snmp_host']} 阶段2 轮询任务完成>>>")
            else:
                # print(f"{item['snmp_host']} 阶段2 轮询任务出错>>>")
                task_logger.error(f"{item['snmp_host']} 阶段2 轮询任务出错>>>")
                # return False
                continue
        return True
    except Exception:
        return False


if __name__ == '__main__':
    pass

