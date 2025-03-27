export function isValidEmail(email: string | undefined): boolean {
	if (!email) return false;
	const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
	return re.test(email);
}
