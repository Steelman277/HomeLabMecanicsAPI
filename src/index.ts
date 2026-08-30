import dotenv from 'dotenv';
import { Client, Events, GatewayIntentBits } from 'discord.js';

dotenv.config({ path: '.env.local' });

const token = process.env.DISCORD_TOKEN;
const craftyUrl = process.env.CRAFTY_URL?.replace(/\/$/, '');
const craftyUsername = process.env.CRAFTY_USERNAME;
const craftyPassword = process.env.CRAFTY_PASSWORD;
const craftyServerId = process.env.CRAFTY_SERVER_ID;
const whitelistChannelId = process.env.WHITELIST_CHANNEL_ID;
const minecraftVerifiedRoleId = process.env.MINECRAFT_VERIFIED_ROLE_ID;

if (!token) {
  throw new Error('DISCORD_TOKEN is missing from .env.local');
}

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

client.on(Events.Error, (error) => {
  console.error('Discord client error:', error);
});

client.once(Events.ClientReady, (readyClient) => {
  console.log(`Logged in as ${readyClient.user.tag}`);
});

async function addToWhitelist(username: string): Promise<void> {
  if (!craftyUrl || !craftyUsername || !craftyPassword || !craftyServerId) {
    throw new Error('Crafty configuration is incomplete');
  }

  const loginResponse = await fetch(`${craftyUrl}/api/v2/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: craftyUsername, password: craftyPassword }),
  });

  if (!loginResponse.ok) {
    throw new Error(`Crafty login failed with HTTP ${loginResponse.status}`);
  }

  const loginData = await loginResponse.json() as { token?: string; access_token?: string };
  const craftyToken = loginData.token ?? loginData.access_token;

  if (!craftyToken) {
    throw new Error('Crafty login response did not contain a token');
  }

  const commandResponse = await fetch(
    `${craftyUrl}/api/v2/servers/${encodeURIComponent(craftyServerId)}/stdin`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${craftyToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ command: `whitelist add ${username}` }),
    },
  );

  if (!commandResponse.ok) {
    throw new Error(`Crafty whitelist request failed with HTTP ${commandResponse.status}`);
  }
}

client.on(Events.MessageCreate, async (message) => {
  if (message.author.bot) return;

  if (message.content === '!ping') {
    await message.reply('Pong!');
    return;
  }

  const isWhitelistCommand = message.content.startsWith('!whitelist');
  const isWhitelistChannel = whitelistChannelId === message.channelId;

  if (!isWhitelistCommand && !isWhitelistChannel) {
    return;
  }
if (isWhitelistCommand) {
  if (!minecraftVerifiedRoleId) {
    await message.reply('Minecraft verified role ID is not configured.');
    return;
  }
if (!message.member || !message.member.roles.cache.has(minecraftVerifiedRoleId)) {
    await message.reply('You must have the Minecraft Verified role to use this command.');
    return;
  }
}

  if (isWhitelistCommand && whitelistChannelId && message.channelId !== whitelistChannelId) {
    await message.reply('Please use the whitelist channel for this command.');
    return;
  }

  const username = isWhitelistCommand
    ? message.content.slice('!whitelist'.length).trim()
    : message.content.trim();

  if (!/^[A-Za-z0-9_]{3,16}$/.test(username)) {
    await message.reply('Enter a valid Minecraft username: 3-16 letters, numbers, or underscores.');
    return;
  }

  try {
    await addToWhitelist(username);
    await message.reply(`${username} was added to the Minecraft whitelist.`);
  } catch (error) {
    console.error('Whitelist request failed:', error);
    await message.reply('I could not update the Minecraft whitelist. Please contact an administrator.');
    await message.reply('This is a dev build of the code so please keep that in mind while testing');
  }
});

client.login(token);
