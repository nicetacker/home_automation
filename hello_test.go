package hello

import (
	"testing"
)

func TestHello(t *testing.T) {
	actual := Greeting("Taro")
	expect := "Hello, Taro"
	if actual != expect {
		t.Errorf("actual %v expect %v", actual, expect)
	}
}