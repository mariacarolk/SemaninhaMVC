lista = [
    {
        'loja': 'Ponto Cruz',
        'dona': 'Dileusa'
    },
    {
        'loja': 'Havan',
        'dona': 'Luciano Hang'
    },
    {
        'loja': 'Água',
        'dona': 'Luciano Hang'
    }
]

# Find index of dictionary with 'loja' = 'Havan'
index = next((i for i, d in enumerate(lista) if d.get('loja') == 'COCO'), -1)

if index != -1:
    print("Index of dictionary with 'loja'':", index)
else:
    print("No dictionary with 'loja' found in the list")