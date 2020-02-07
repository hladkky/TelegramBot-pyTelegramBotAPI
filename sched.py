weekdays = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П\'ятниця']

bmd, web, cm, oop, bi, en = 'Обробка та аналіз БМД', 'Веб-технології та веб-дизайн',\
                            'Чисельні методи', 'ООП', 'Біоінформатика-1. Основи МББ', 'Іноземна мова'

bmdT = [
    'професор Настенко Євгеній Арнольдович',
    'доцент Носовець Олена Костянтинівна',
    'асистент Давидько Олександр Богданович',
    'асистент Матвійчук Олександр Вадимович'
]

webT = [
    'доцент Соломін Андрій В\'ячеславович',
    'асистент Матвійчук Олександр Вадимович'
]

cmT = [
    'доцент Клен Катерина Сергіївна',
    'доцент Абакумова Олена Олегівна'
]

oopT = [
    'доцент Алхімова Світлана Миколаївна',
    'асистент Уманець Віталій Сергійович',
    'асистент Рисін Сергій Валентинович'
]

biT = [
    'старший викладач Кисляк Сергій Володимирович'
]

enT = [
    'старший викладач Компанець Наталія Михайлівна'
]

lessons = bmd, web, cm, oop, bi, en
teachers = bmdT, webT, cmT, oopT, biT, enT

pr, lc, lb = 'Практика', 'Лекція', 'Лабораторна'

DICT = {
    '1': {
        0: [[bmd, bmdT[2:4], '12-а-31', pr],
            [web, webT[0], '327-24', lc],
            [cm, cmT[:], '402-12', lb]],
        1: [[oop, oopT[0:], '402-24', lc],
            [bi, biT[0:], '4-23янг-Пол.', pr],
            [oop, oopT[1:3], '33-13', pr]],
        2: [[web, webT[-1:], '24-31', pr],
            [bmd, bmdT[0:], '402-24', lc],
            [bi, biT[0:], '402-24', lc],
            ['ФП', '', '', '']],
        3: [[bmd, bmdT[1:4], '12-а-31', pr],
            [en, enT[0:], '12-а-31', pr],
            [cm, cmT[1:], '301-12', lc]],
        4: [[cm, cmT[0:], '304-12', pr],
            [bi, biT[0:], '4-23янг-Пол', pr],
            [bi, biT[0:], '402-24', lc]]
    },
    '2': {
        0: [[oop, oopT[1:3], '33-13', pr],
            [web, webT[0:1], '327-24', lc],
            [cm, cmT[:], '402-12', lb]],
        1: [[oop, oopT[0:1], '402-24', lc],
            [bi, biT[0:1], '4-23янг-Пол.', pr],
            [oop, oopT[1:3], '33-13', pr]],
        2: [[web, webT[-1:0], '24-31', pr],
            [bmd, bmdT[0:], '402-24', lc],
            ['', '', '', ''],
            ['ФП', '', '', '']],
        3: [[bmd, bmdT[1:4], '12-а-31', pr],
            [en, enT[0:], '12-а-31', pr],
            [cm, cmT[1:], '301-12', lc]],
        4: [[cm, cmT[0:], '304-12', pr],
            [bi, biT[0:], '4-23янг-Пол', pr],
            [bi, biT[0:], '402-24', lc]]
    }
}
