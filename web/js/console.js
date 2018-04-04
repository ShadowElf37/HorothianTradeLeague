var IOCN_TYPE = "span";
var IOCN_STYLE = {
    'b': {fontWeight: "bold"},
    'i': {fontStyle: "italic"},
    'u': {textDecoration: "underline"},
    'c': {},
    'C': {}
};
var IOCN_FMTS = {
    'c': "color",
    'C': "backgroundColor"
};

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
  * console function .clrfmt() clears formatting
  * .format(str, ...) emits formatting, where str has CSS as described in IOCN_STYLE, and any character in IOCN_FMTS has the corresponding property set to the next argument to fmt
  * Example: .format('bC', '#aaaaaa') makes any following text bold and gray
***/

function CHistory(max) {
    this.ohistory = [];
    this.history = [''];
    this.pos = 0;
    this.max = max;
}
CHistory.prototype.up = function(old) {
    if(this.pos == 0)
        return old;
    this.history[this.pos--] = old;
    return this.history[this.pos];
}
CHistory.prototype.down = function(old) {
    if(this.pos == this.history.length)
        return old;
    this.history[this.pos++] = old;
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
    this.container = container || outnode;
    
    this.input = document.createElement(IOCN_TYPE);
    this.input.contentEditable = "true";
    this.input.autofocus = true;
    this.input.innerHTML = "&#8203;";
    this.input.focus();
    
    this.outputter = new Outputter(outnode, this.input);
    this.caller.console(this.outputter);
    this.outputter.print(this.caller.prompt());
    
    this.history = new CHistory(1000);
    
    var self = this;
    window.addEventListener('keypress', function(ev) {
        self.onkey(ev);
    });
    window.addEventListener('click', function(ev) {
        if(self.container.contains(ev.target))
            self.input.focus();
    });
}
IOConsole.prototype.onkey = function(ev) {
    if(!this.container.contains(ev.target))
        return false;
    var text = this.input.innerText.replace(String.fromCharCode(8203), '');
    var args = text.replace(/^\s+|\s+$/g, "").split(/\s+/);
    var cmd = args.shift();
    
    switch(ev.key) {
    case "Enter":
        this.outputter.println(text);
        this.history.commit(text);
        if(cmd){
            this.caller.call(cmd, args, this.input);
        }
        else {
            this.outputter.print(this.caller.prompt());
            this.input.innerHTML = "&#8203;";
            this.input.focus();
        }
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

function Outputter(outn, input) {
    this.outnode = outn;
    this.input = input;
    this._chfn();
}

Outputter.prototype._newline = function(c) {
    c.appendChild(document.createElement('br'));
}
Outputter.prototype._print = function(c, str) {
    if(str)
        c.appendChild(document.createTextNode(str));
}
Outputter.prototype.print = function(str) {
    if(!str)
        return;
    var child = document.createElement(IOCN_TYPE);
    var lines = str.split(/\r?\n/);
    this._print(child, lines[0]);
    for(var i=1;i<lines.length;i++) {
        this._newline(child);
        this._print(child, lines[i]);
    }
    this.fnode.insertBefore(child, this.input);
}
Outputter.prototype.println = function(str) {
    this.print((str || "") + '\n');
}
Outputter.prototype._chfn = function(fn) {
    this.fnode = document.createElement(IOCN_TYPE);
    this.outnode.appendChild(this.fnode);
    this.fnode.appendChild(this.input);
}

Outputter.prototype._objcp = function(dest, src) {
    if(!src || !dest)
        return;
    for(var i in src)
    {
        console.log(i, src[i]);
        dest[i] = src[i];
        console.log(dest[i]);
    }
}
Outputter.prototype.format = function() {
    var args = Array.prototype.slice.call(arguments);
    var str = args.shift() || "";
    this._chfn();
    for(var i=0;i<str.length;i++)
    {
        this._objcp(this.fnode.style, IOCN_STYLE[str[i]]); // deepcopy
        var interp = IOCN_FMTS[str[i]];
        if(interp)
            this.fnode.style[interp] = args.shift();
    }
}
Outputter.prototype.clrfmt = function() {
    this.format("");
}
