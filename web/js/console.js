var IOCN_TYPE = "span";

/***
  * IOConsole interface:
  * instantiate with `new IOConsole(caller, outnode[, container])`
  * outnode is the node where the magic happens
  * container is the object click to get focus of the console
    * defaults to outnode
  * caller is an object with attributes:
    * .console(cons): console object is passed here on initialization
    * .call(func, args): calls the function w/ args `args`
    * .prompt(): return the current prompt for the console
  * the console has output functions print() and println(), pass UTF-8 strings please
***/

function CHistory(max) {
    this.ohistory = [];
    this.history = [''];
    this.pos = 0;
    this.max = max;
}
CHistory.prototype.up = function(old) {
    console.log(this.history, this.pos);
    if(this.pos == 0)
        return old;
    this.history[this.pos--] = old;
    console.log(this.history, this.pos);
    return this.history[this.pos];
}
CHistory.prototype.down = function(old) {
    console.log(this.history, this.pos);
    if(this.pos == this.history.length)
        return old;
    this.history[this.pos++] = old;
    console.log(this.history, this.pos);
    return this.history[this.pos];
}
CHistory.prototype.commit = function(cmd) {
    if(!cmd.match(/^\s/) && cmd !== this.ohistory[this.ohistory.length - 1])
    {
        this.ohistory.push(cmd);
        if(this.ohistory.length > this.max)
            this.ohistory.shift();
        this.history = Array.from(this.ohistory);
        this.history.push("");
    }
    this.pos = this.ohistory.length;
}

function IOConsole(caller, outnode, container) {
    if(!outnode)
        throw "Invalid outnode!";
    this.caller = caller;
    this.outnode = outnode;
    this.container = container || this.outnode; 
    console.log(this.container);
    
    this.input = document.createElement(IOCN_TYPE);
    this.input.contentEditable = "true";
    this.input.autofocus = true;
    this.input.focus();
    this.outnode.appendChild(this.input);
    
    this.history = new CHistory(1000);
    
    var self = this;
    window.addEventListener('keypress', function(ev) {
        self.onkey(ev);
    });
    window.addEventListener('click', function(ev) {
        if(self.container.contains(ev.target))
            console.log(self.input);
            self.input.focus();
    });
    this.caller.console(this);
    this.print(this.caller.prompt());
}
IOConsole.prototype.onkey = function(ev) {
    if(!this.container.contains(ev.target))
        return false;
    var text = this.input.innerText;
    var args = text.replace(/^\s+|\s+$/g, "").split(/\s+/);
    var cmd = args.shift();
    
    switch(ev.key) {
    case "Enter":
        this.println(text);
        this.history.commit(text);
        if(cmd)
            this.caller.call(cmd, args);
        this.print(this.caller.prompt());
        this.input.innerHTML = "";
        ev.preventDefault();
        break;
    case "ArrowDown":
        this.input.innerText = this.history.down(text);
        break;
    case "ArrowUp":
        this.input.innerText = this.history.up(text);
        break;
    default:
        console.log(ev.key);
    }
    return false;
}

IOConsole.prototype._newline = function(c) {
    c.appendChild(document.createElement('br'));
}
IOConsole.prototype._print = function(c, str) {
    if(str)
        c.appendChild(document.createTextNode(str));
}
IOConsole.prototype.print = function(str) {
    if(!str)
        return;
    var child = document.createElement(IOCN_TYPE);
    var lines = str.split(/\r?\n/);
    this._print(child, lines[0]);
    for(var i=1;i<lines.length;i++) {
        this._newline(child);
        this._print(child, lines[i]);
    }
    this.outnode.insertBefore(child, this.input);
}
IOConsole.prototype.println = function(str) {
    this.print((str || "") + '\n');
}
