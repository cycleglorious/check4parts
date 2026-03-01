export const load = async ({ params }) => {
	const { id } = params;

	return {
		part: {
			name: 'КОМПЛЕКТ РЕМЕНЯ ГРМ' + id,
			description: 'Комплект ременя ГРМ SCHAEFFLER INA 530 0650 10',
			brand: {
				id: '1',
				name: 'SCHAEFFLER INA' + id
			},
			details: [
				{ id: '1', value: '1234', title: 'Деталь 1', name: 'detail_1' },
				{ id: '2', value: '5678', title: 'Деталь 2', name: 'detail_2' }
			],
			id: 'VND5300650' + id,
			code: 'INA530065010' + id,
			image: '/image 7.png'
		},
		crosses: [
			{
				id: '1',
				name: 'VAG',
				code: 'VAG123456',
				image: '/image 7.png',
				quantity_in_pack: 1,
				group: 'Група 1',
				brand: 'Бренд 1'
			},
			{
				id: '2',
				name: 'MERCEDES-BENZ',
				code: 'MB654321',
				quantity_in_pack: 2,
				group: 'Група 2',
				brand: 'Бренд 2'
			}
		],
		additional: [
			{
				id: '1',
				name: 'VAG',
				code: 'VAG123456',
				min_quantity: 1
			},
			{
				id: '2',
				name: 'MERCEDES-BENZ',
				code: 'MB654321',
				min_quantity: 2
			}
		],
		rests: [
			{
				id: '1',
				provider: {
					id: '1',
					name: 'Постачальник 1'
				},
				quantity: 10,
				delivery_time: '2 дні',
				price: 100
			},
			{
				id: '2',
				provider: {
					id: '2',
					name: 'Постачальник 2'
				},
				quantity: 5,
				delivery_time: '3 дні',
				price: 150
			}
		]
	};
};
