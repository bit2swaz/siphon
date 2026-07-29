// segmentio/kafka-go Writer
package events

import (
	"context"

	"github.com/segmentio/kafka-go"
	"google.golang.org/protobuf/proto"

	siphonpb "github.com/bit2swaz/siphon/proto/gen/go/siphon"
)

// UserEventData is defined in types.go (same package).

type KafkaPublisher struct {
	writer *kafka.Writer
}

func NewKafkaPublisher(bootstrap, topic string) *KafkaPublisher {
	return &KafkaPublisher{
		writer: &kafka.Writer{
			Addr:                   kafka.TCP(bootstrap),
			Topic:                  topic,
			Balancer:               &kafka.LeastBytes{},
			RequiredAcks:           kafka.RequireAll,
			AllowAutoTopicCreation: false,
		},
	}
}

func (k *KafkaPublisher) Publish(e UserEventData) error {
	msg := &siphonpb.UserEvent{
		UserId:    e.UserID,
		VideoId:   e.VideoID,
		EventType: e.EventType,
		Timestamp: e.Timestamp,
		WatchFrac: e.WatchFrac,
	}
	b, err := proto.Marshal(msg)
	if err != nil {
		return err
	}
	return k.writer.WriteMessages(context.Background(), kafka.Message{
		Key:   []byte(e.UserID),
		Value: b,
	})
}
