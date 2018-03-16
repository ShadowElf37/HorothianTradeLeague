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
            this.output.println("You just killed " + (args.join(' ') || 'yourself') + '!');
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
    if(func)
        func.call(this, args);
    else
        // Send to server
        this.def(cmd, args);
}
