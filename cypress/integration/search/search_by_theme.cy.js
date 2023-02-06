
describe("searching datasets by SASDI themes", ()=>{

    beforeEach(()=>{
        cy.visit("/dataset/")
    })

    it("search datasets by organization", ()=>{
        cy.get("#headSASDIThemes")
        .click()
        .get("#SASDIThemes").click()
        .get(".dataset-item").its("length").should("gt",0)
    })


})
