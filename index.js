const Discord = require('discord.js');
const bot = new Discord.Client();
const token = 'NzA4NDUzMjI0OTg5OTgyNzMx.XrXkmQ.S_GUwYjmx2csDn6uDN6KWJbGePw';

bot.on('ready', () => {
    console.log('This bot is online');
});

bot.on('message', msg => {
    if (msg.content == "hello") {
        msg.reply('Hello friend!');
    }
});

bot.login(token);
