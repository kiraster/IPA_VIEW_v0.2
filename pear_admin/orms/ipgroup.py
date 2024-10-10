from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from pear_admin.extensions import db

from ._base import BaseORM


class IPGroupORM(BaseORM):
    __tablename__ = "ip_group"

    id = db.Column(db.Integer, primary_key=True, comment="自增id")
    group_name = db.Column(db.String(256), unique=True, comment="分组名称")
    # group_item = db.relationship('IPTableORM', backref='group', lazy=True)  # 建立外键关联

    # 定义双向访问，可返回包含iptable表的json数据，不经过views函数进行处理
    ip_tables = db.relationship('IPTableORM', back_populates="ip_group")  # 建立外键关联

    def json(self):
        return {
            "id": self.id,
            "group_name": self.group_name,
            "ip_tables": [ip_table.json() for ip_table in self.ip_tables]
        }

    def json_for_tree(self):
        return {
            "title": self.group_name,
            "children": [ip_table.json_for_tree() for ip_table in self.ip_tables]
        }

    def json_for_setting(self):
        return {
            "id": self.id,
            "group_name": self.group_name,
        }
