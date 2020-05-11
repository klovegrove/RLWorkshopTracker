const siteURL = 'https://steamcommunity.com/workshop/browse/?appid=252950&browsesort=trend&section=readytouseitems&actualsort=trend&p=1&days=-1';
const axios = require('axios');

const fetchData = async () => {
    const result = await axios.get(siteURL);
    return cheerio.load(result.data);
}