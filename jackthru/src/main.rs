use std::io;

fn main() {
    let (client, _status) =
        jack::Client::new("chipmouse.thru",
                          jack::ClientOptions::NO_START_SERVER).unwrap();

    let mut output = client
        .register_port("output",
                       jack::MidiOut::default())
        .unwrap();
    let input = client
        .register_port("input",
                       jack::MidiIn::default())
        .unwrap();

    let cback = move |_: &jack::Client, ps: &jack::ProcessScope| -> jack::Control {
        let events = input.iter(ps);
        let mut send = output.writer(ps);

        for event in events {
            let _ = send.write(&event).unwrap();
        }

        jack::Control::Continue
    };

    let active_client = client
        .activate_async((), jack::ClosureProcessHandler::new(cback))
        .unwrap();

    let mut user_input = String::new();
    io::stdin().read_line(&mut user_input).ok();

    active_client.deactivate().unwrap();
}
