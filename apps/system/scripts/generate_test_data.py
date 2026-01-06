from faker import Faker
from system.models import faker_data  
fake = Faker()

for _ in range(100):
    FakerData.objects.create(
        name=fake.name(),
        created_at=fake.date_time_between(start_date='-1y', end_date='now')
    )
