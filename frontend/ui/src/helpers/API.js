import axios from "axios";
export class API {
  set config(config) {
    this._config = config;
  }
  get config() {
    return this._config ?? {};
  }
  get instance() {
    if (!this._instance) {
      this._instance = axios.create(this.config);
    }

    return this._instance;
  }

  setHeaderOnInstance(key, value) {
    this.instance.defaults.headers[key] = value;
  }

  async login(credentials) {
    const { data } = await this.instance.post("/auth/login/", credentials);

    return data;
  }

  async logout() {
    const { data } = await this.instance.get("/auth/logout/");

    return data;
  }

  async getUser() {
    const { data } = await this.instance.get("/auth/user/");

    return data;
  }

  async getAssets() {
    const { data } = await this.instance.get("/assets/");
    return data;
  }

  async getInitialAdvice() {
    const { data } = await this.instance.get("/assets/advice/");

    return data;
  }

  async getAdvice(risk, amount) {
    const { data } = await this.instance.get(
      `/assets/advice/?investing_sum=${amount}&risk_level=${risk}`
    );

    return data;
  }

  async getWallets() {
    const { data } = await this.instance.get("/wallets/");
    return data;
  }

  async getWallet(id) {
    const { data } = await this.instance.get(`/wallets/${id}/transactions/`);
    return data;
  }

  async getAsset(name) {
    const { data } = await this.instance.get(`/assets/${name}/stat/`);

    return data;
  }

  async postAssets(assets) {
    const { data } = await this.instance.post(`/assets/`, assets);

    return data;
  }
}

const service = new API();

service.config = {
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    common: {
      Authorization: localStorage.getItem("AUTH_TOKEN") ?? "",
    },
  },
};

export default service;
