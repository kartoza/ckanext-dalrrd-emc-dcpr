// describe("login to emc local instance", ()=>{
//     beforeEach(()=>{
//         cy.visit("/") // http://localhost:5000 added as baseURL to cypress.json config file
//     })
//     it("logs in to EMC_dcpr system", ()=>{
//         cy.get("[data-testid='nav_login']").click()
//         .url().should('include', 'user/login')
//         .get("#field-login")
//         .type("admin")
//         .should("have.value","admin")
//         .get("#field-password")
//         .type("12345678")
//         .should("have.value","12345678")
//         .get(".btn-primary").click() // change this
//         .url().should('include', 'dashboard')
//         .get("[data-testid='loggedin_user_icon']")
//         .click()
//         .get("[data-testid='logout']")
//         .click()
//         .url().should("include","/user")
//         .get("[data-testid='nav_login']").contains("Log in")
//     })

// })


describe("search for datasets via title", ()=>{
    it("tests from the home page by text",()=>{
        cy.visit("/")
        cy.get("[data-testid='home_dataset_search_input']")
        .type("test dataset no.1")
        .url().should("include","/dataset/?q=dataset+no.1")
        // cy.get("data-testid=['search_item_anchor']")
        // .nextSibling.innerHTML.contains("test dataset")


    })
})
