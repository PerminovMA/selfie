
from Server.models import User, Token
User.objects.create(name = name, email = email, sex = sex, age = age, token = token)
import random, string

def random_str(count_chars=TOKEN_LEN):
    return ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in xrange(count_chars))

i = 0
while i < 100:
	age_range = random.choice([User.AGE_RANGE_1, User.AGE_RANGE_2, User.AGE_RANGE_3])
	sex = random.choice([User.MALE, User.FEMALE])
	token = Token.objects.create(token = 'some_token')
	name = random_str(10)
	email = random_str(40)
	city = random.choice(['Moscow', 'Tula', 'SPb', 'Monchegorsk', 'Novgorod', 'Murmansk'])
	country = random.choice(['Russia', 'USA', 'France', 'England'])

	User.objects.create(name = name, email = email, sex = sex, age = age_range, token = token, city = city, country = country)
	i += 1