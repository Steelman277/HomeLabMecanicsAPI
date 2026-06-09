const { Client, GatewayIntentBits, REST, Routes, SlashCommandBuilder } = require('discord.js');
const axios = require('axios');
require('dotenv').config();

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// Register slash command
const commands = [
  new SlashCommandBuilder()
    .setName('whitelist')
    .setDescription('Whitelist a player')
    .addStringOption(opt =>
      opt.setName('username')
        .setDescription('Player username')
        .setRequired(true))
].map(cmd => cmd.toJSON());

const rest = new REST({ version: '10' }).setToken(process.env.BOT_TOKEN);

(async () => {
  await rest.put(
    Routes.applicationGuildCommands(process.env.CLIENT_ID, process.env.GUILD_ID),
    { body: commands }
  );
  console.log('Commands registered');
})();

// Handle the command
client.on('interactionCreate', async interaction => {
  if (!interaction.isChatInputCommand()) return;
  if (interaction.commandName !== 'whitelist') return;

  const username = interaction.options.getString('username');

  // Optional: restrict to specific roles
  const allowedRole = 'Admin';
  if (!interaction.member.roles.cache.some(r => r.name === allowedRole)) {
    return interaction.reply({ content: '❌ No permission.', ephemeral: true });
  }

  try {
    await interaction.deferReply();

    // Send to your server's API
    const response = await axios.post(
      `${process.env.SERVER_API_URL}/whitelist`,
      { username },
      { headers: { 'Authorization': `Bearer ${process.env.SERVER_API_KEY}` } }
    );

    await interaction.editReply(`✅ **${username}** has been whitelisted!`);
  } catch (err) {
    await interaction.editReply(`❌ Failed: ${err.response?.data?.message || err.message}`);
  }
});

client.login(process.env.BOT_TOKEN);