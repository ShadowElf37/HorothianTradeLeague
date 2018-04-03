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
SimpleCmd.prototype.call = function(cmd, args) {
    var func = this.functions[cmd];
    var self = this;
    if(func)
        func.call(this, args);
    else
        fetch("http://[[host]]:[[port]]/cmd/" + cmd + '/' + args.join('-')).then(function(response) {
            response.text().then(function(text) {
                t = text.split('|')
                style = t[0];
                color = t[1];
                text = t.slice(2).join('|').split('\n');
                self.output.format(style, color);
                for (i=0; i<text.length; i++){
                    self.output.println(text[i]);
                }
                self.output.clrfmt();
            });
        });
        //this.def(cmd, args);
}
