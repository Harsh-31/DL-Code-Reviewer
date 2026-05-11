// sample.v — 8-bit counter with intentional issues for review testing

module counter (
    input        clk,
    input        rst,
    output reg [7:0] count
);

// BUG 1: Blocking assignment (=) used in sequential always block
// BUG 2: Overflow not handled — wraps silently
// BUG 3: No async reset; synchronous reset but poorly structured
// BUG 4: No output enable or load functionality

always @(posedge clk) begin
    if (rst)
        count = 8'd0;       // should be <=
    else
        count <= count + 1; // mixing blocking and non-blocking
end

endmodule
