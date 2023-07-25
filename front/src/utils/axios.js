import axios from 'axios';

const private_axios = axios.create({
    baseURL: 'http://localhost:8000',
    headers: { 'Content-Type': 'application/json' }
});

const public_axios = axios.create({
    baseURL: 'http://localhost:8000',
    headers: { 'Content-Type': 'application/json' }
});