from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from pear_admin.extensions import db

from ._base import BaseORM


class IPTableORM(BaseORM):
    __tablename__ = "ip_table"

    id = db.Column(db.Integer, primary_key=True, comment="自增id")
    ip = db.Column(db.String(15), comment="IP地址")
    mask = db.Column(db.String(15), comment="子网掩码")
    mac_add = db.Column(db.String(17), comment="MAC地址")
    network = db.Column(db.String(18), comment="网段")
    system_name = db.Column(db.String(256), comment="设备名称")
    snmp_host = db.Column(db.String(15), comment="snmp轮询地址")
    vlan = db.Column(db.String(5), comment="vlan")
    port_name = db.Column(db.String(256), comment="端口名称")
    desc = db.Column(db.String(256), comment="描述")
    user = db.Column(db.String(256), comment="使用人")
    available = db.Column(db.Boolean, default=False, comment="在线状态")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ip_group_id = db.Column(db.Integer, db.ForeignKey('ip_group.id'), default=1, comment="分组id")  # 建立外键关联

    # 定义双向访问，可返回包含group_name的json数据，不经过views函数进行处理
    ip_group = db.relationship("IPGroupORM", back_populates="ip_tables")

    def json(self):
        return {
            "id": self.id,
            "ip": self.ip,
            "mask": self.mask,
            "mac_add": self.mac_add,
            "network": self.network,
            "system_name": self.system_name,
            "snmp_host": self.snmp_host,
            "vlan": self.vlan,
            "port_name": self.port_name,
            "desc": self.desc,
            "user": self.user,
            "available": self.available,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "group_name": self.ip_group.group_name
        }

    def json_for_tree(self):
        return {
            "id": self.network,
            "title": self.network
        }

    def json_for_transfer(self):
        return {
            "id": self.id,
            "network": self.network
        }
