package main

import (
	"fmt"
	"time"

	"github.com/mixcode/broadlink"
)

type irCode []byte

type broadlinkBlaster struct {
	device *broadlink.Device
}

func DiscoverBlaster() (*broadlinkBlaster, error) {
	// Discover devices
	devs, _ := broadlink.DiscoverDevices(1*time.Second, 0)
	if len(devs) == 0 {
		return nil, fmt.Errorf("device not found") 
	}

	// Auth 
	dev := devs[0]
	myname := "my test server"    // Your local machine's name.
	myid := make([]byte, 15)      // Must be 15 bytes long.
	err := dev.Auth(myid, myname) // d.ID and d.AESKey will be updated on success.
	if err != nil {
		return nil, err
	}
	return &broadlinkBlaster {
		device : &dev,
	}, nil
}

func (b *broadlinkBlaster) capture() (irCode, error) {
	err := b.device.StartCaptureRemoteControlCode()
	if err != nil {
		return nil, fmt.Errorf("Capture start failed: %v", err)
	}

	// Poll captured data. (Certainly you can do much better than this ;p)
	var rtype broadlink.RemoteType
	var ircode irCode

	ok := false
	for i := 0; i < 30; i++ {
		rtype, ircode, err = b.device.ReadCapturedRemoteControlCode()
		if err == nil {
			ok = true
			break
		}
		if err != broadlink.ErrNotCaptured {
			return nil, err
		}
		time.Sleep(time.Second)
		continue
	}

	if !ok {
		return nil, fmt.Errorf("learn timeout)")
	}
	fmt.Printf("rtype %v, ircode %v, err %v\n", rtype, ircode, err)

	return ircode, nil
}

func (b *broadlinkBlaster) send(code irCode) error {
	return b.device.SendIRRemoteCode(code, 1)
}
