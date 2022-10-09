import random
import re
from dataclasses import asdict
from enum import Enum
from xml.dom.minidom import parseString

from dicttoxml import dicttoxml
from faker import Faker

from classes.order import Order, Article, OrderA, OrderB, OrderC
from classes.receipt import Receipt
from classes.initiate import Initiate
from classes.stream import Stream
from classes.order_status import OrderStatus, OrderStatusA, OrderStatusB, Status
from classes.product import Product, ProductA
from classes.part import PartB, PartC


def dict_factory(data) -> dict:
    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.name.lower()
        return obj

    return dict((k, convert_value(v)) for k, v in data)


def write_xml(folder: str, number: int, obj: any) -> None:
    obj_dict = asdict(obj, dict_factory=dict_factory)
    class_name = obj.__class__.__name__
    # To snake case
    class_name = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()

    xml = dicttoxml(obj_dict, attr_type=False, custom_root=class_name)
    dom = parseString(xml)

    file_name = f"{folder}{class_name}_{number}.xml"
    f = open(file_name, "w+")
    f.write(dom.toprettyxml())
    f.close()


def generate_xml(folder: str) -> None:
    random.seed(0)
    Faker.seed(0)
    fake = Faker()

    for i in range(10):
        order = Order(
            i,
            random.choice(list(Article)),
            random.randint(1, 10),
            fake.address(),
            fake.unix_time(),
        )

        receipt = Receipt(i, fake.first_name(), fake.pricetag())

        initiate = Initiate(
            fake.random_number(5, fix_len=True), fake.company(), fake.unix_time()
        )
        stream = Stream(i, fake.sentence(nb_words=5))

        write_xml(folder, i, order)
        write_xml(folder, i, receipt)
        write_xml(folder, i, initiate)
        write_xml(folder, i, stream)


def generate_supply_chain_xml(folder: str) -> None:
    random.seed(1)
    Faker.seed(1)
    fake = Faker()

    for i in range(10):
        order_a = OrderA(i, fake.random_number(2, fix_len=True), fake.unix_time())
        order_b = OrderB(i, random.randint(1, 10), fake.unix_time())
        order_c = OrderC(
            i, fake.random_number(2, fix_len=True), fake.company(), fake.unix_time(),
        )

        order_status = OrderStatus(i, random.choice(list(Status)))
        order_status_a = OrderStatusA(i, random.choice(list(Status)))
        order_status_b = OrderStatusB(i, random.choice(list(Status)))

        product = Product(i, fake.pricetag())
        product_a = ProductA(i, fake.address(), fake.pricetag())

        part_b = PartB(i, fake.address(), fake.pricetag())
        part_c = PartC(i, fake.address(), fake.pricetag())

        write_xml(folder, i, order_a)
        write_xml(folder, i, order_b)
        write_xml(folder, i, order_c)

        write_xml(folder, i, order_status)
        write_xml(folder, i, order_status_a)
        write_xml(folder, i, order_status_b)

        write_xml(folder, i, product)
        write_xml(folder, i, product_a)

        write_xml(folder, i, part_b)
        write_xml(folder, i, part_c)


if __name__ == "__main__":
    generate_xml("./../correlator/message-templates/")
    generate_supply_chain_xml("./../correlator/message-templates/")
