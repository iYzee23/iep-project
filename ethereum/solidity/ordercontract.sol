pragma solidity ^0.8.18;

contract OrderContract {
    address payable owner;
    address payable courier = payable(address(0));
    address customer;

    bool paid = false;
    bool ended = false;

    modifier onlyCustomer() {
        require(msg.sender == customer, "Invalid customer account.");
        _;
    }

    modifier mustBeJoinedCourier() {
        require(courier != payable(address(0)), "Delivery not complete.");
        _;
    }

    modifier mustPayCustomer() {
        require(paid, "Transfer not complete.");
        _;
    }

    modifier haventPaidCustomer() {
        require(!paid, "Transfer already complete.");
        _;
    }

    modifier notEnded() {
        require(!ended, "Pickup already complete.");
        _;
    }

    constructor(address cust) {
        owner = payable(msg.sender);
        customer = cust;
    }

    function customerPaid() external payable onlyCustomer haventPaidCustomer notEnded {
        paid = true;
    }

    function orderDelivered() external onlyCustomer mustPayCustomer mustBeJoinedCourier notEnded  {
        ended = true;
        courier.transfer(address(this).balance * 20 / 100);
        owner.transfer(address(this).balance * 80 / 100);
    }

    function courierJoined(address payable cour) external mustPayCustomer notEnded {
        courier = cour;
    }
}