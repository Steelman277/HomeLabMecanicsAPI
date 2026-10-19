"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const dotenv_1 = __importDefault(require("dotenv"));
const discord_js_1 = require("discord.js");
const undici_1 = require("undici");
dotenv_1.default.config({ path: '.env.local' });
const token = process.env.DISCORD_TOKEN;
const craftyUrl = process.env.CRAFTY_URL?.replace(/\/$/, '');
const craftyUsername = process.env.CRAFTY_USERNAME;
const craftyPassword = process.env.CRAFTY_PASSWORD;
const craftyServerId = process.env.CRAFTY_SERVER_ID;
const logChannelId = process.env.LOG_CHANNEL_ID;
const craftyAgent = new undici_1.Agent({
    connect: {
        rejectUnauthorized: process.env.CRAFTY_TLS_REJECT_UNAUTHORIZED !== 'false',
    },
});
const whitelistChannelId = process.env.WHITELIST_CHANNEL_ID;
const minecraftVerifiedRoleId = process.env.MINECRAFT_VERIFIED_ROLE_ID;
const minecraftWhitelistedRoleId = process.env.MINECRAFT_WHITELISTED_ROLE_ID;
const POLL_INTERVAL = 5000;
let lastLogLength;
let cachedCraftyToken;
let isPollingLogs = false;
if (!token) {
    throw new Error('DISCORD_TOKEN is missing from .env.local');
}
const client = new discord_js_1.Client({
    intents: [
        discord_js_1.GatewayIntentBits.Guilds,
        discord_js_1.GatewayIntentBits.GuildMembers,
        discord_js_1.GatewayIntentBits.GuildMessages,
        discord_js_1.GatewayIntentBits.MessageContent,
    ],
});
client.on(discord_js_1.Events.Error, (error) => {
    console.error('Discord client error:', error);
});
client.once(discord_js_1.Events.ClientReady, (readyClient) => {
    console.log(`Logged in as ${readyClient.user.tag}`);
    void runLogPoll();
    setInterval(() => {
        void runLogPoll();
    }, POLL_INTERVAL);
});
async function addToWhitelist(username) {
    if (!craftyUrl || !craftyServerId) {
        throw new Error('Crafty configuration is incomplete');
    }
    const craftyToken = await getCraftyToken();
    const commandResponse = await (0, undici_1.fetch)(`${craftyUrl}/api/v2/servers/${encodeURIComponent(craftyServerId)}/stdin`, {
        method: 'POST',
        dispatcher: craftyAgent,
        headers: {
            Authorization: `Bearer ${craftyToken}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: `Whitelist add ${username}` }),
    });
    if (!commandResponse.ok) {
        if (commandResponse.status === 401)
            cachedCraftyToken = undefined;
        throw new Error(`Crafty whitelist request failed with HTTP ${commandResponse.status}`);
    }
}
async function getCraftyToken() {
    if (cachedCraftyToken)
        return cachedCraftyToken;
    if (!craftyUrl || !craftyUsername || !craftyPassword) {
        throw new Error('Crafty configuration is incomplete');
    }
    const loginResponse = await (0, undici_1.fetch)(`${craftyUrl}/api/v2/auth/login`, {
        method: 'POST',
        dispatcher: craftyAgent,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: craftyUsername, password: craftyPassword }),
    });
    if (!loginResponse.ok) {
        throw new Error(`Crafty login failed with HTTP ${loginResponse.status}`);
    }
    const loginData = await loginResponse.json();
    const craftyToken = findCraftyToken(loginData);
    if (!craftyToken) {
        const responseKeys = loginData && typeof loginData === 'object'
            ? Object.keys(loginData).join(', ')
            : typeof loginData;
        throw new Error(`Crafty login response did not contain a token (fields: ${responseKeys || 'none'})`);
    }
    cachedCraftyToken = craftyToken;
    return craftyToken;
}
function findCraftyToken(value) {
    if (!value || typeof value !== 'object')
        return undefined;
    for (const [key, nestedValue] of Object.entries(value)) {
        if (['token', 'access_token', 'accessToken'].includes(key) && typeof nestedValue === 'string') {
            return nestedValue;
        }
        const nestedToken = findCraftyToken(nestedValue);
        if (nestedToken)
            return nestedToken;
    }
    return undefined;
}
async function pollLogs() {
    if (!craftyUrl || !craftyServerId) {
        throw new Error('Crafty configuration is incomplete');
    }
    const craftyToken = await getCraftyToken();
    const response = await (0, undici_1.fetch)(`${craftyUrl}/api/v2/servers/${encodeURIComponent(craftyServerId)}/logs`, {
        dispatcher: craftyAgent,
        headers: { Authorization: `Bearer ${craftyToken}` },
    });
    if (!response.ok) {
        if (response.status === 401)
            cachedCraftyToken = undefined;
        throw new Error(`Crafty logs request failed with HTTP ${response.status}`);
    }
    const payload = await response.json();
    if (!payload || typeof payload !== 'object' || !('data' in payload) || !Array.isArray(payload.data)) {
        throw new Error('Crafty logs response did not contain a data array');
    }
    const lines = payload.data.filter((line) => typeof line === 'string');
    if (lastLogLength === undefined || lines.length < lastLogLength) {
        lastLogLength = lines.length;
        return;
    }
    const newLines = lines.slice(lastLogLength);
    lastLogLength = lines.length;
    for (const line of newLines) {
        const joinedPlayer = line.match(/: (\w+) joined the game/)?.[1];
        if (joinedPlayer) {
            await postToDiscord(`✅ **${joinedPlayer}** joined the server.`);
        }
        const leftPlayer = line.match(/: (\w+) left the game/)?.[1];
        if (leftPlayer) {
            await postToDiscord(`👋 **${leftPlayer}** left the server.`);
        }
    }
}
async function runLogPoll() {
    if (isPollingLogs)
        return;
    isPollingLogs = true;
    try {
        await pollLogs();
    }
    catch (error) {
        console.error('Log polling failed:', error);
    }
    finally {
        isPollingLogs = false;
    }
}
async function postToDiscord(message) {
    if (!logChannelId) {
        throw new Error('LOG_CHANNEL_ID is missing from .env.local');
    }
    const channel = await client.channels.fetch(logChannelId);
    if (!channel || !channel.isTextBased() || !('send' in channel)) {
        throw new Error('Configured log channel cannot receive messages');
    }
    await channel.send(message);
}
client.on(discord_js_1.Events.MessageCreate, async (message) => {
    if (message.author.bot)
        return;
    if (message.content === '!ping') {
        await message.reply('Pong!');
        return;
    }
    const isWhitelistCommand = /^!whitelist(?:\s|$)/i.test(message.content);
    const isWhitelistChannel = whitelistChannelId === message.channelId;
    if (!isWhitelistCommand && !isWhitelistChannel) {
        return;
    }
    if (!whitelistChannelId) {
        await message.reply('Whitelist channel ID is not configured.');
        return;
    }
    if (isWhitelistCommand && message.channelId !== whitelistChannelId) {
        await message.reply('Please use the whitelist channel for this command.');
        return;
    }
    if (!minecraftVerifiedRoleId) {
        await message.reply('Minecraft verified role ID is not configured.');
        return;
    }
    if (!message.member || !message.member.roles.cache.has(minecraftVerifiedRoleId)) {
        await message.reply('You must have the Minecraft Verified role to use this command.');
        return;
    }
    const username = isWhitelistCommand
        ? message.content.replace(/^!whitelist\s*/i, '').trim()
        : message.content.trim();
    if (!/^[A-Za-z0-9_]{3,16}$/.test(username)) {
        await message.reply('Enter a valid Minecraft username: 3-16 letters, numbers, or underscores.');
        return;
    }
    try {
        await addToWhitelist(username);
        if (!minecraftWhitelistedRoleId || !message.member) {
            throw new Error('Whitelisted role or guild member is not configured');
        }
        await message.member.roles.add(minecraftWhitelistedRoleId);
        await message.reply(`${username} was added to the Minecraft whitelist and received the role.`);
    }
    catch (error) {
        console.error('Whitelist request failed:', error);
        await message.reply('I could not update the Minecraft whitelist. Please contact an administrator.');
    }
});
client.login(token);
