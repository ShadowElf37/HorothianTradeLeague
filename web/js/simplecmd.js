function SimpleCmd() {
    this.output = null;
    this.helpstr = "Type help for help.";
    this.functions = {
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
SimpleCmd.prototype.call = function(cmd, args, input) {
    this.waiting = true;
    var func = this.functions[cmd];
    var self = this;
    this.input = input;
    if(func) {
        self.output.println(cmd + ' ' + args.join(' '));
        func.call(this, args);
        self.output.print(self.prompt());
        self.input.contentEditable = "true";
        self.input.innerHTML = "&#8203;";
        self.input.focus();
        }
    else {
        this.input.contentEditable = "false";
        fetch("http://[[host]]:[[port]]/cmd/" + cmd + '/' + args.join('-')).then(function(response) {
            response.text().then(function(text) {
                t = text.split('|')
                style = t[0];
                color = t[1];
                text = t.slice(2).join('|').split('\n');
                self.output.println(cmd + ' ' + args.join(' '));
                self.output.format(style, color);
                for (i=0; i<text.length; i++){
                    self.output.println(text[i]);
                }
                self.output.clrfmt();
                self.output.print(self.prompt());
                self.input.contentEditable = "true";
                self.input.innerHTML = "&#8203;";
                self.input.focus();
            });
        });

    }
        //this.def(cmd, args);
}
