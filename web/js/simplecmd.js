function SimpleCmd() {
    this.output = null;
    this.helpstr = "Type help for help.";
    this.functions = {
        "help": function(args) {
            this.output.println("Commands:");
            this.output.println("help - this");
            this.output.println("kill - kill <arg>");
        },
        "kill": function(args) {
            this.output.format('bic', '#ff0000');
            this.output.println("You just killed " + (args.join(' ') || 'yourself') + '!');
            this.output.clrfmt();
        }
    }
}

SimpleCmd.prototype.prompt = function() {
    return " $ ";
}

SimpleCmd.prototype.console = function(o) {
    this.output = o;
}

SimpleCmd.prototype.def = function(cmd, args) {
    this.output.println("Unknown command " + cmd + ". " + this.helpstr);
}
SimpleCmd.prototype.call = function(cmd, args) {
    var func = this.functions[cmd];
    var self = this;
    if(func)
        func.call(this, args);
    else
        fetch("http://[[host]]:[[port]]/cmd/" + cmd + '/' + args.join('-')).then(function(response) {
            response.text().then(function(text) {
                console.log(text);
                style = text.split('|')[0];
                color = text.split('|')[1];
                text = text.split('|')[2];
                console.log(text);
                self.output.format(style, color);
                self.output.println(text);
                self.output.clrfmt();
            });
        });
        //this.def(cmd, args);
}
