from address import Address
from mailing import Mailing

mailing = Mailing(to_address=Address("32323", "МСК", "Маяковская", "2", "34"),
                  from_address=Address("55533", "СПБ", "Набережная", "5", "47"),
                  cost=500,
                  track="RU1290012")

print(
    f"Отправление {mailing.track} "
    f"из {mailing.from_address.index}, {mailing.from_address.city}, "
    f"{mailing.from_address.street}, {mailing.from_address.house} - {mailing.from_address.apartment} "
    f"в {mailing.to_address.index}, {mailing.to_address.city}, "
    f"{mailing.to_address.street}, {mailing.to_address.house} - {mailing.to_address.apartment}. "
    f"Стоимость {mailing.cost} рублей."
)
