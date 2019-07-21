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

func TestHello2(t *testing.T) {
	actual := Greeting("Taro")
	expect := "Hello, Hoge"
	if actual != expect {
		t.Errorf("actual %v expect %v", actual, expect)
	}
}