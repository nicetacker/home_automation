package main

import (
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/nlopes/slack"
)

const (
	discoverRetry = 3
	mapFile = "./data/map_file.dat"
)

// SlackListener replesents slack client
type SlackListener struct {
	client    *slack.Client
	botID     string
	channelID string
	device    *broadlinkBlaster
	db        *commandDB
}

// CreateSlackListener returns slack listenner
func CreateSlackListener(token string, id string, channel string) *SlackListener {
	var device *broadlinkBlaster
	var err error

	// Discover device
	for i:=0; i<discoverRetry; i++ {
		device, err = DiscoverBlaster()
		if err != nil {
			log.Printf("[ERROR] discover fail : %v / %v", err)
			time.Sleep(time.Second)
			continue
		}
		break
	}

	// Create DB
	commandDB, err := CreateDB(mapFile)
	if err != nil {
		log.Printf("[ERROR] db create : %v", err)
	}

	// Create SlackListener
	client := slack.New(token)
	ret := &SlackListener{
		client:    client,
		botID:     id,
		channelID: channel,
		device : device,
		db: commandDB,
	}
	return ret
}

// ListenAndResponse listen slack events and response
// particuler messages.
func (s *SlackListener) ListenAndResponse() {
	rtm := s.client.NewRTM()
	go rtm.ManageConnection()

	for msg := range rtm.IncomingEvents {
		switch ev := msg.Data.(type) {
		case *slack.MessageEvent:
			if err := s.handleMessageEvent(ev); err != nil {
				log.Printf("[ERROR] failed to handle message: %s", err)
			}
		default:
			log.Printf("Event: %v ", ev)
		}
	}
}

func (s *SlackListener) handleMessageEvent(ev *slack.MessageEvent) error {
	if ev.Channel != s.channelID {
		log.Printf("[DEBUG] channel id is wrong. %s (expect %s): %s", ev.Channel, s.channelID, ev.Msg.Text)
		return nil
	}

	msg := strings.TrimSpace(ev.Msg.Text)
	if msg == "" {
		// for IFTTT
		msg = strings.TrimSpace(ev.Attachments[0].Pretext)
	}

	m := strings.Split(msg, " ")
	if len(m) == 0 {
		return fmt.Errorf("invalid message: %s", msg)
	}

	switch m[0] {
	case "req":
		for _, cmd := range m[1:] {
			ir, err := s.db.get(cmd)
			if err != nil {
				return err
			}
			fmt.Printf("request cmd= %v.\n", cmd)
			s.device.send(ir)
			time.Sleep(time.Second)
		}
		return nil
	case "learn":
		cmd := m[1]
		ircode, err := s.device.capture()
		if err == nil {
			fmt.Printf("capture success")
			err = s.db.set(cmd, ircode)
		}
		return err
	default:
		return fmt.Errorf("invalid command")
	}
}
