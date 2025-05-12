import type { PageLoad } from './$types';

export const load: PageLoad = ({ url }) => {
	let searchParams = url.searchParams;
	let search = searchParams.get('q');
	console.log(search);
};
