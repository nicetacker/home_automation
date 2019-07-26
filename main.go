package main

import (
	"log"

	"github.com/kelseyhightower/envconfig"
)

type envConfig struct {
	BotToken  string `envconfig:"BOT_TOKEN" required:"true"`
	ChannelID string `envconfig:"CHANNEL_ID" required:"true"`
}

func main() {
	var env envConfig
	if err := envconfig.Process("", &env); err != nil {
		log.Printf("[ERROR] Failed to process env var: %s", err)
		return 
	}

	log.Printf("[INFO] Start slack event listening")
	SlackListener := CreateSlackListener(env.BotToken, env.ChannelID, env.ChannelID)
	SlackListener.ListenAndResponse()
}
