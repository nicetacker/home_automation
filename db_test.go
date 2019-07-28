package main

import (
	"os"
	"testing"
)

func Test_DB(t *testing.T) {
	// SetUp
	os.Remove("/tmp/valid_path")
	os.Create("/tmp/broken_data")
	defer os.Remove("/tmp/broken_data")

	tests := []struct {
		name    string
		path    string
		wantErr bool
	}{
		{
			name:    "invalid path should fail",
			path:    "/no/such/path",
			wantErr: true,
		},
		{
			name:    "file create",
			path:    "/tmp/valid_path",
			wantErr: false,
		},
		{
			name:    "broken data -> file create",
			path:    "/tmp/broken_data",
			wantErr: false,
		},
	}
	for _, tt := range tests {
		db, err := CreateDB(tt.path)
		if (err != nil) != tt.wantErr {
			t.Errorf("%v error = %v, wantErr %v", tt.name, err, tt.wantErr)
		}

		if tt.wantErr == false {
			code := make(irCode, 10)
			if _, e := db.get("aircon.on"); e == nil {
				t.Errorf("%v: get on empty db should fail\n", tt.name)
			}

			if e := db.set("aircon.on", code); e != nil {
				t.Errorf("%v: set should success\n", tt.name)
			}

			if _, e := db.get("aircon.on"); e != nil {
				t.Errorf("%v: get should success\n", tt.name)
			}

			if _, e := db.get("aircon.off"); e == nil {
				t.Errorf("%v: get on empty db should fail\n", tt.name)
			}
		}
	}
}
