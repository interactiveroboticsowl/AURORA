import createClient from 'openapi-fetch';
import type { paths } from './v1';
import { API_BASE_URL } from '../config';

const client = createClient<paths>({ baseUrl: `${API_BASE_URL}/` });
export default client;
