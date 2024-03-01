from datetime import date, datetime

birth_date = '2009-02-13'
today = date.today()
authorized_age = 15

birth = datetime.strptime(birth_date, '%Y-%m-%d')
print(f'Aujourd\'hui année:  {today.year}, mois: {today.month}, day: {today.day}')
print(f'Année naissance:  {birth.year}, mois: {birth.month}, day: {birth.day}')
print(f'Authorized: {authorized_age}')

accepted_register = True

if today.year - birth.year >= authorized_age:
    if today.year - birth.year == authorized_age:
        if today.month >= birth.month:
            if today.month == birth.month:
                if today.day < birth.day:
                    accepted_register = False

if accepted_register:
    print(f'L\'utilisateur es autorisé car il a plus de 15 ans: {today.year - birth.year} ans')
else:
    print(f'L\'utilisateur est refusé car il est trop jeune: {today.year - birth.year} ans')
